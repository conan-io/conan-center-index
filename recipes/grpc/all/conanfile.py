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
    generators = "cmake", "cmake_find_package"
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

    def requirements(self):
        self.requires('zlib/1.2.11')
        self.requires('openssl/1.1.1k')
        self.requires('protobuf/3.15.5')
        self.requires('c-ares/1.17.1')
        self.requires('abseil/20210324.0')
        self.requires('re2/20210202')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os in ['Windows', 'Linux']:
            raise ConanInvalidConfiguration('WIP! Testing systems one by one')

        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio":
            compiler_version = tools.Version(self.settings.compiler.version)
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)

        # This doesn't work yet as one would expect, because the install target builds everything
        # and we need the install target because of the generated CMake files
        #
        #   enable_mobile=False # Enables iOS and Android support
        #
        # cmake.definitions["CONAN_ENABLE_MOBILE"] = "ON" if self.options.build_csharp_ext else "OFF"


        cmake.definitions["gRPC_BUILD_CODEGEN"] = bool(self.options.build_codegen)
        cmake.definitions["gRPC_BUILD_CSHARP_EXT"] = bool(self.options.build_csharp_ext)
        cmake.definitions["gRPC_BUILD_TESTS"] = False

        # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
        cmake.definitions["gRPC_INSTALL"] = True
        # cmake.definitions["CMAKE_INSTALL_PREFIX"] = self._build_subfolder

        # tell grpc to use the find_package versions
        cmake.definitions["gRPC_ZLIB_PROVIDER"] = "package"
        cmake.definitions["gRPC_CARES_PROVIDER"] = "package"
        cmake.definitions["gRPC_RE2_PROVIDER"] = "package"
        cmake.definitions["gRPC_SSL_PROVIDER"] = "package"
        cmake.definitions["gRPC_PROTOBUF_PROVIDER"] = "package"
        cmake.definitions["gRPC_ABSL_PROVIDER"] = "package"

        cmake.definitions["gRPC_BUILD_GRPC_CPP_PLUGIN"] = bool(self.options.build_cpp_plugin)
        cmake.definitions["gRPC_BUILD_GRPC_CSHARP_PLUGIN"] = bool(self.options.build_csharp_plugin)
        cmake.definitions["gRPC_BUILD_GRPC_NODE_PLUGIN"] = bool(self.options.build_node_plugin)
        cmake.definitions["gRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN"] = bool(self.options.build_objective_c_plugin)
        cmake.definitions["gRPC_BUILD_GRPC_PHP_PLUGIN"] = bool(self.options.build_php_plugin)
        cmake.definitions["gRPC_BUILD_GRPC_PYTHON_PLUGIN"] = bool(self.options.build_python_plugin)
        cmake.definitions["gRPC_BUILD_GRPC_RUBY_PLUGIN"] = bool(self.options.build_ruby_plugin)

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
    
    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.cpp_info.names["cmake_find_package"] = "gRPC"
        self.cpp_info.names["cmake_find_package_multi"] = "gRPC"

        # gRPC::address_sorting
        self.cpp_info.components["address_sorting"].names["cmake_find_package"] = "address_sorting"
        self.cpp_info.components["address_sorting"].names["cmake_find_package_multi"] = "address_sorting"
        self.cpp_info.components["address_sorting"].system_libs = ["m", "pthread"]
        self.cpp_info.components["address_sorting"].libs = ["address_sorting"]

        # gRPC::gpr
        self.cpp_info.components["gpr"].names["cmake_find_package"] = "gpr"
        self.cpp_info.components["gpr"].names["cmake_find_package_multi"] = "gpr"
        self.cpp_info.components["gpr"].requires = ["abseil::absl_base", "abseil::absl_memory", "abseil::absl_status", "abseil::absl_str_format", "abseil::absl_strings", "abseil::absl_synchronization", "abseil::absl_time", "abseil::absl_optional"]
        self.cpp_info.components["gpr"].system_libs = ["m", "pthread"]
        self.cpp_info.components["gpr"].libs = ["gpr"]

        # gRPC::grpc
        self.cpp_info.components["_grpc"].names["cmake_find_package"] = "grpc"
        self.cpp_info.components["_grpc"].names["cmake_find_package_multi"] = "grpc"
        self.cpp_info.components["_grpc"].requires = ["zlib::zlib", "c-ares::cares", "address_sorting", "re2::re2", "upb", "abseil::absl_flat_hash_map", "abseil::absl_inlined_vector", "abseil::absl_bind_front", "abseil::absl_statusor", "gpr", "openssl::ssl", "openssl::crypto", "address_sorting", "upb"]
        self.cpp_info.components["_grpc"].frameworks = ["CoreFoundation"]
        self.cpp_info.components["_grpc"].system_libs = ["m", "pthread"]
        self.cpp_info.components["_grpc"].libs = ["grpc"]

        # gRPC::grpc_unsecure
        self.cpp_info.components["grpc_unsecure"].names["cmake_find_package"] = "grpc_unsecure"
        self.cpp_info.components["grpc_unsecure"].names["cmake_find_package_multi"] = "grpc_unsecure"
        self.cpp_info.components["grpc_unsecure"].requires = ["zlib::zlib", "c-ares::cares", "address_sorting", "re2::re2", "upb", "abseil::absl_flat_hash_map", "abseil::absl_inlined_vector", "abseil::absl_statusor", "gpr", "address_sorting", "upb"]
        self.cpp_info.components["grpc_unsecure"].frameworks = ["CoreFoundation"]
        self.cpp_info.components["grpc_unsecure"].system_libs = ["m", "pthread"]
        self.cpp_info.components["grpc_unsecure"].libs = ["grpc_unsecure"]

        # gRPC::grpc++
        self.cpp_info.components["grpc++"].names["cmake_find_package"] = "grpc++"
        self.cpp_info.components["grpc++"].names["cmake_find_package_multi"] = "grpc++"
        self.cpp_info.components["grpc++"].requires = ["protobuf::libprotobuf", "_grpc"]
        self.cpp_info.components["grpc++"].system_libs = ["m", "pthread"]
        self.cpp_info.components["grpc++"].libs = ["grpc++"]

        # gRPC::grpc++_alts
        self.cpp_info.components["grpc++_alts"].names["cmake_find_package"] = "grpc++_alts"
        self.cpp_info.components["grpc++_alts"].names["cmake_find_package_multi"] = "grpc++_alts"
        self.cpp_info.components["grpc++_alts"].requires = ["protobuf::libprotobuf", "grpc++"]
        self.cpp_info.components["grpc++_alts"].system_libs = ["m", "pthread"]
        self.cpp_info.components["grpc++_alts"].libs = ["grpc++_alts"]

        # gRPC::grpc++_error_details
        self.cpp_info.components["grpc++_error_details"].names["cmake_find_package"] = "grpc++_error_details"
        self.cpp_info.components["grpc++_error_details"].names["cmake_find_package_multi"] = "grpc++_error_details"
        self.cpp_info.components["grpc++_error_details"].requires = ["protobuf::libprotobuf", "grpc++"]
        self.cpp_info.components["grpc++_error_details"].system_libs = ["m", "pthread"]
        self.cpp_info.components["grpc++_error_details"].libs = ["grpc++_error_details"]

        # gRPC::grpc++_reflection
        self.cpp_info.components["grpc++_reflection"].names["cmake_find_package"] = "grpc++_reflection"
        self.cpp_info.components["grpc++_reflection"].names["cmake_find_package_multi"] = "grpc++_reflection"
        self.cpp_info.components["grpc++_reflection"].requires = ["protobuf::libprotobuf", "grpc++"]
        self.cpp_info.components["grpc++_reflection"].system_libs = ["m", "pthread"]
        self.cpp_info.components["grpc++_reflection"].libs = ["grpc++_reflection"]

        # gRPC::grpc++_unsecure
        self.cpp_info.components["grpc++_unsecure"].names["cmake_find_package"] = "grpc++_unsecure"
        self.cpp_info.components["grpc++_unsecure"].names["cmake_find_package_multi"] = "grpc++_unsecure"
        self.cpp_info.components["grpc++_unsecure"].requires = ["protobuf::libprotobuf", "grpc_unsecure"]
        self.cpp_info.components["grpc++_unsecure"].system_libs = ["m", "pthread"]
        self.cpp_info.components["grpc++_unsecure"].libs = ["grpc++_unsecure"]

        # gRPC::grpc_plugin_support
        self.cpp_info.components["grpc_plugin_support"].names["cmake_find_package"] = "grpc_plugin_support"
        self.cpp_info.components["grpc_plugin_support"].names["cmake_find_package_multi"] = "grpc_plugin_support"
        self.cpp_info.components["grpc_plugin_support"].requires = ["protobuf::libprotoc", "protobuf::libprotobuf"]
        self.cpp_info.components["grpc_plugin_support"].system_libs = ["m", "pthread"]
        self.cpp_info.components["grpc_plugin_support"].libs = ["grpc_plugin_support"]

        # gRPC::grpcpp_channelz
        self.cpp_info.components["grpcpp_channelz"].names["cmake_find_package"] = "grpcpp_channelz"
        self.cpp_info.components["grpcpp_channelz"].names["cmake_find_package_multi"] = "grpcpp_channelz"
        self.cpp_info.components["grpcpp_channelz"].requires = ["protobuf::libprotobuf",  "_grpc"]
        self.cpp_info.components["grpcpp_channelz"].system_libs = ["m", "pthread"]
        self.cpp_info.components["grpcpp_channelz"].libs = ["grpcpp_channelz"]

        # gRPC::upb
        self.cpp_info.components["upb"].names["cmake_find_package"] = "upb"
        self.cpp_info.components["upb"].names["cmake_find_package_multi"] = "upb"
        self.cpp_info.components["upb"].system_libs = ["m", "pthread"]
        self.cpp_info.components["upb"].libs = ["upb"]

        # Executables
        # gRPC::grpc_cpp_plugin
        # gRPC::grpc_csharp_plugin
        # gRPC::grpc_node_plugin
        # gRPC::grpc_objective_c_plugin
        # gRPC::grpc_php_plugin
        # gRPC::grpc_python_plugin
        # gRPC::grpc_ruby_plugin

        """
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["wsock32", "ws2_32", "crypt32"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "rt", "m", "pthread"]
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.system_libs = ["m", "pthread"]
        if self.settings.os == "Android":
            self.cpp_info.system_libs = ["m"]
        """
