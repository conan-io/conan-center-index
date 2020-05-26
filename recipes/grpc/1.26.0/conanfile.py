from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class grpcConan(ConanFile):
    name = "grpc"
    version = "1.26.0"
    description = "Google's RPC library and framework."
    topics = ("conan", "grpc", "rpc")
    url = "https://github.com/inexorgame/conan-grpc"
    homepage = "https://github.com/grpc/grpc"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt", "add_rpath.patch", "b54a5b338637f92bfcf4b0bc05e0f57a5fd8fadd.patch"]
    generators = "cmake", "cmake_find_package_multi"
    short_paths = True
    keep_imports = True

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_codegen": [True, False],
        "build_csharp_ext": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_codegen": True,
        "build_csharp_ext": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "zlib/1.2.11",
        "openssl/1.1.1d",
        "protobuf/3.9.1",
        "protoc/3.9.1",
        "c-ares/1.15.0"
    )

    def imports(self):
        # when built with protobuf:shared=True, grpc plugins will require its libraries to run
        # so we copy those from protobuf package
        if tools.os_info.is_linux:
            # `ldd` shows dependencies named like libprotoc.so.3.9.1.0
            self.protobuf_dylib_mask = "*.so.*"
        else:
            assert False, "grpc package was not checked on your system"
        self.copy(self.protobuf_dylib_mask, dst="lib", src="lib", root_package="protobuf")

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = tools.Version(self.settings.compiler.version)
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        # This patch adds RPATH to grpc plugins binaries for correct work with dynamically built protobuf
        tools.check_with_algorithm_sum("sha1", "add_rpath.patch", "a6467f92d93a9550e9876ea487c49a24bd34ad97")
        tools.patch(base_path=self._source_subfolder, patch_file="add_rpath.patch", strip=1)

        # This patch refers to https://github.com/grpc/grpc/commit/b54a5b338637f92bfcf4b0bc05e0f57a5fd8fadd and helps to avoid hungs during test
        tools.check_with_algorithm_sum("sha1", "b54a5b338637f92bfcf4b0bc05e0f57a5fd8fadd.patch", "56818a07d0a9b47a32ed65577be777eb224f5c78")
        tools.patch(base_path=self._source_subfolder, patch_file="b54a5b338637f92bfcf4b0bc05e0f57a5fd8fadd.patch", strip=1)

        cmake_path = os.path.join(self._source_subfolder, "CMakeLists.txt")

        # See #5
        tools.replace_in_file(cmake_path, "_gRPC_PROTOBUF_LIBRARIES", "CONAN_LIBS_PROTOBUF")

        # See https://github.com/grpc/grpc/issues/21293 - OpenSSL 1.1.1+ doesn't work without
        tools.replace_in_file(
            cmake_path, "set(_gRPC_BASELIB_LIBRARIES wsock32 ws2_32)", "set(_gRPC_BASELIB_LIBRARIES wsock32 ws2_32 crypt32)")

        # cmake_find_package_multi is producing a c-ares::c-ares target, grpc is looking for c-ares::cares
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "cmake", "cares.cmake"), "c-ares::cares", "c-ares::c-ares")

        # Parts which should be options:
        # grpc_cronet
        # grpc++_cronet
        # grpc_unsecure (?)
        # grpc++_unsecure (?)
        # grpc++_reflection
        # gen_hpack_tables (?)
        # gen_legal_metadata_characters (?)
        # grpc_csharp_plugin
        # grpc_node_plugin
        # grpc_objective_c_plugin
        # grpc_php_plugin
        # grpc_python_plugin
        # grpc_ruby_plugin

    def _configure_cmake(self):
        cmake = CMake(self)

        # This doesn't work yet as one would expect, because the install target builds everything
        # and we need the install target because of the generated CMake files
        #
        #   enable_mobile=False # Enables iOS and Android support
        #   non_cpp_plugins=False # Enables plugins such as --java-out and --py-out (if False, only --cpp-out is possible)
        #
        # cmake.definitions['CONAN_ADDITIONAL_PLUGINS'] = "ON" if self.options.build_csharp_ext else "OFF"
        #
        # Doesn't work yet for the same reason as above
        #
        # cmake.definitions['CONAN_ENABLE_MOBILE'] = "ON" if self.options.build_csharp_ext else "OFF"


        cmake.definitions['gRPC_BUILD_CODEGEN'] = "ON" if self.options.build_codegen else "OFF"
        cmake.definitions['gRPC_BUILD_CSHARP_EXT'] = "ON" if self.options.build_csharp_ext else "OFF"
        #cmake.definitions['gRPC_BUILD_TESTS'] = "OFF"

        # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
        cmake.definitions['gRPC_INSTALL'] = "ON"
        # cmake.definitions['CMAKE_INSTALL_PREFIX'] = self._build_subfolder

        # tell grpc to use the find_package versions
        cmake.definitions['gRPC_CARES_PROVIDER'] = "package"
        cmake.definitions['gRPC_ZLIB_PROVIDER'] = "package"
        cmake.definitions['gRPC_SSL_PROVIDER'] = "package"
        cmake.definitions['gRPC_PROTOBUF_PROVIDER'] = "package"

        # Compilation on minGW GCC requires to set _WIN32_WINNTT to at least 0x600
        # https://github.com/grpc/grpc/blob/109c570727c3089fef655edcdd0dd02cc5958010/include/grpc/impl/codegen/port_platform.h#L44
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-D_WIN32_WINNT=0x600"
            cmake.definitions["CMAKE_C_FLAGS"] = "-D_WIN32_WINNT=0x600"

        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="LICENSE", dst="licenses")
        self.copy('*', dst='include', src='{}/include'.format(self._source_subfolder))
        self.copy('*.cmake', dst='lib', src='{}/lib'.format(self._build_subfolder), keep_path=True)
        self.copy("*.lib", dst="lib", src="", keep_path=False)
        self.copy("*.a", dst="lib", src="", keep_path=False)
        self.copy("*", dst="bin", src="bin")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy(self.protobuf_dylib_mask, dst="lib", src="lib")

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.libs = [
            "grpc++_unsecure",
            "grpc++_reflection",
            "grpc++_error_details",
            "grpc++",
            "grpc_unsecure",
            "grpc_plugin_support",
            "grpc_cronet",
            "grpcpp_channelz",
            "grpc",
            "gpr",
            "address_sorting",
            "upb",
        ]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.system_libs += ["wsock32", "ws2_32"]
