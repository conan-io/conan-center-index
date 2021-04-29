from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class grpcConan(ConanFile):
    name = "grpc"
    description = "Google's RPC library and framework."
    topics = ("conan", "grpc", "rpc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/grpc/grpc"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "cmake_find_package_multi"
    short_paths = True

    settings = "os", "arch", "compiler", "build_type"
    # TODO: Add shared option
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_codegen": [True, False],
        "build_csharp_ext": [True, False],
        "build_cpp_plugin": [True, False],
        "build_csharp_plugin": [True, False],
        "build_node_plugin": [True, False],
        "build_objective_c_plugin": [True, False],
        "build_php_plugin": [True, False],
        "build_python_plugin": [True, False],
        "build_ruby_plugin": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_codegen": True,
        "build_csharp_ext": False,
        "build_cpp_plugin": True,
        "build_csharp_plugin": True,
        "build_node_plugin": True,
        "build_objective_c_plugin": True,
        "build_php_plugin": True,
        "build_python_plugin": True,
        "build_ruby_plugin": True,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "zlib/1.2.11",
        "openssl/1.1.1h",
        "protobuf/3.13.0",
        "c-ares/1.15.0",
        "abseil/20200225.3",
        "re2/20201101"
    )

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
            compiler_version = tools.Version(self.settings.compiler.version)
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

        # See #5
        cmake_path = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmake_path, "_gRPC_PROTOBUF_LIBRARIES", "CONAN_LIBS_PROTOBUF")

    def _configure_cmake(self):
        cmake = CMake(self)

        # This doesn't work yet as one would expect, because the install target builds everything
        # and we need the install target because of the generated CMake files
        #
        #   enable_mobile=False # Enables iOS and Android support
        #
        # cmake.definitions["CONAN_ENABLE_MOBILE"] = "ON" if self.options.build_csharp_ext else "OFF"


        cmake.definitions["gRPC_BUILD_CODEGEN"] = "ON" if self.options.build_codegen else "OFF"
        cmake.definitions["gRPC_BUILD_CSHARP_EXT"] = "ON" if self.options.build_csharp_ext else "OFF"
        cmake.definitions["gRPC_BUILD_TESTS"] = "OFF"

        # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
        cmake.definitions["gRPC_INSTALL"] = "ON"
        # cmake.definitions["CMAKE_INSTALL_PREFIX"] = self._build_subfolder

        # tell grpc to use the find_package versions
        cmake.definitions["gRPC_ZLIB_PROVIDER"] = "package"
        cmake.definitions["gRPC_CARES_PROVIDER"] = "package"
        cmake.definitions["gRPC_RE2_PROVIDER"] = "package"
        cmake.definitions["gRPC_SSL_PROVIDER"] = "package"
        cmake.definitions["gRPC_PROTOBUF_PROVIDER"] = "package"
        cmake.definitions["gRPC_ABSL_PROVIDER"] = "package"

        cmake.definitions["gRPC_BUILD_GRPC_CPP_PLUGIN"] = self.options.build_cpp_plugin
        cmake.definitions["gRPC_BUILD_GRPC_CSHARP_PLUGIN"] = self.options.build_csharp_plugin
        cmake.definitions["gRPC_BUILD_GRPC_NODE_PLUGIN"] = self.options.build_node_plugin
        cmake.definitions["gRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN"] = self.options.build_objective_c_plugin
        cmake.definitions["gRPC_BUILD_GRPC_PHP_PLUGIN"] = self.options.build_php_plugin
        cmake.definitions["gRPC_BUILD_GRPC_PYTHON_PLUGIN"] = self.options.build_python_plugin
        cmake.definitions["gRPC_BUILD_GRPC_RUBY_PLUGIN"] = self.options.build_ruby_plugin

        # see https://github.com/inexorgame/conan-grpc/issues/39
        if self.settings.os == "Windows":
            if not self.options["protobuf"].shared:
                cmake.definitions["Protobuf_USE_STATIC_LIBS"] = "ON"
            else:
                cmake.definitions["PROTOBUF_USE_DLLS"] = "ON"

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        #cmake.install()

        # tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        # tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
    
    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.cpp_info.names["cmake_find_package"] = "gRPC"
        self.cpp_info.names["cmake_find_package_multi"] = "gRPC"

        self.cpp_info.libs = [
            "grpc++_unsecure",
            "grpc++_reflection",
            "grpc++_error_details",
            "grpc++",
            "grpc_unsecure",
            "grpc_plugin_support",
            "grpcpp_channelz",
            "grpc",
            "gpr",
            "address_sorting",
            "upb",
        ]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["wsock32", "ws2_32", "crypt32"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "rt", "m", "pthread"]
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.system_libs = ["m", "pthread"]
        if self.settings.os == "Android":
            self.cpp_info.system_libs = ["m"]
