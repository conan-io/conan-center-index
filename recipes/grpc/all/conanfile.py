from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class grpcConan(ConanFile):
    name = "grpc"
    description = "Google's RPC (remote procedure call) library and framework."
    topics = ("grpc", "rpc")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/grpc/grpc"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    # TODO: Add shared option
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "codegen": [True, False],
        "csharp_ext": [True, False],
        "cpp_plugin": [True, False],
        "csharp_plugin": [True, False],
        "node_plugin": [True, False],
        "objective_c_plugin": [True, False],
        "php_plugin": [True, False],
        "python_plugin": [True, False],
        "ruby_plugin": [True, False],
        "secure": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "codegen": True,
        "csharp_ext": False,
        "cpp_plugin": True,
        "csharp_plugin": True,
        "node_plugin": True,
        "objective_c_plugin": True,
        "php_plugin": True,
        "python_plugin": True,
        "ruby_plugin": True,
        "secure": False,
    }

    short_paths = True
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _grpc_plugin_template(self):
        return "grpc_plugin_template.cmake.in"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        self.copy(os.path.join("cmake", self._grpc_plugin_template))
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires('zlib/1.2.11')
        self.requires('openssl/1.1.1m')
        self.requires('protobuf/3.19.2')
        self.requires('c-ares/1.17.2')
        self.requires('abseil/20211102.0')
        self.requires('re2/20211101')

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            compiler_version = tools.Version(self.settings.compiler.version)
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")

        if self.options.shared:
            # FIXME: try to support grpc shared and abseil static with gcc on Linux
            # current error while linking internal check_epollexclusive executable:
            # libabsl_time.a(duration.cc.o): undefined reference to symbol '_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7compareEPKc@@GLIBCXX_3.4.21'
            if (self.settings.os == "Linux" and self.settings.compiler == "gcc") and not self.options["abseil"].shared:
                raise ConanInvalidConfiguration(
                    "gRPC shared not supported yet without abseil shared"
                )

            if self._is_msvc:
                raise ConanInvalidConfiguration(
                    "gRPC shared not supported yet with {} on {}".format(self.settings.compiler, self.settings.os)
                )

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        del self.info.options.secure

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires('protobuf/3.19.2')
            # when cross compiling we need pre compiled grpc plugins for protoc
            if tools.cross_building(self):
                self.build_requires('grpc/{}'.format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake

        # This doesn't work yet as one would expect, because the install target builds everything
        # and we need the install target because of the generated CMake files
        #
        #   enable_mobile=False # Enables iOS and Android support
        #
        # cmake.definitions["CONAN_ENABLE_MOBILE"] = "ON" if self.options.csharp_ext else "OFF"

        self._cmake = CMake(self)
        self._cmake.definitions["gRPC_BUILD_CODEGEN"] = self.options.codegen
        self._cmake.definitions["gRPC_BUILD_CSHARP_EXT"] = self.options.csharp_ext
        self._cmake.definitions["gRPC_BUILD_TESTS"] = False

        # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
        self._cmake.definitions["gRPC_INSTALL"] = True

        # tell grpc to use the find_package versions
        self._cmake.definitions["gRPC_ZLIB_PROVIDER"] = "package"
        self._cmake.definitions["gRPC_CARES_PROVIDER"] = "package"
        self._cmake.definitions["gRPC_RE2_PROVIDER"] = "package"
        self._cmake.definitions["gRPC_SSL_PROVIDER"] = "package"
        self._cmake.definitions["gRPC_PROTOBUF_PROVIDER"] = "package"
        self._cmake.definitions["gRPC_ABSL_PROVIDER"] = "package"

        self._cmake.definitions["gRPC_BUILD_GRPC_CPP_PLUGIN"] = self.options.cpp_plugin
        self._cmake.definitions["gRPC_BUILD_GRPC_CSHARP_PLUGIN"] = self.options.csharp_plugin
        self._cmake.definitions["gRPC_BUILD_GRPC_NODE_PLUGIN"] = self.options.node_plugin
        self._cmake.definitions["gRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN"] = self.options.objective_c_plugin
        self._cmake.definitions["gRPC_BUILD_GRPC_PHP_PLUGIN"] = self.options.php_plugin
        self._cmake.definitions["gRPC_BUILD_GRPC_PYTHON_PLUGIN"] = self.options.python_plugin
        self._cmake.definitions["gRPC_BUILD_GRPC_RUBY_PLUGIN"] = self.options.ruby_plugin

        # Some compilers will start defaulting to C++17, so abseil will be built using C++17
        # gRPC will force C++11 if CMAKE_CXX_STANDARD is not defined
        # So, if settings.compiler.cppstd is not defined there will be a mismatch
        if not tools.valid_min_cppstd(self, 11):
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = 11

        if tools.cross_building(self):
            # otherwise find_package() can't find config files since
            # conan doesn't populate CMAKE_FIND_ROOT_PATH
            self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_PACKAGE"] = "BOTH"

        if tools.is_apple_os(self.settings.os):
            # workaround for: install TARGETS given no BUNDLE DESTINATION for MACOSX_BUNDLE executable
            self._cmake.definitions["CMAKE_MACOSX_BUNDLE"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # We are fine with protobuf::protoc coming from conan generated Find/config file
        # TODO: to remove when moving to CMakeToolchain (see https://github.com/conan-io/conan/pull/10186)
        tools.replace_in_file(os.path.join(self._source_subfolder, "cmake", "protobuf.cmake"),
            "find_program(_gRPC_PROTOBUF_PROTOC_EXECUTABLE protoc)",
            "set(_gRPC_PROTOBUF_PROTOC_EXECUTABLE $<TARGET_FILE:protobuf::protoc>)"
        )
        if tools.Version(self.version) >= "1.39.0" and tools.Version(self.version) < "1.42.0":
            # Bug introduced in https://github.com/grpc/grpc/pull/26148
            # Reverted in https://github.com/grpc/grpc/pull/27626
            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                    "if(gRPC_INSTALL AND NOT CMAKE_CROSSCOMPILING)",
                    "if(gRPC_INSTALL)")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        # Create one custom module file per executable in order to emulate
        # CMake executables imported targets of grpc
        for plugin_option, values in self._grpc_plugins.items():
            if self.options.get_safe(plugin_option):
                target = values["target"]
                executable = values["executable"]
                self._create_executable_module_file(target, executable)

    @property
    def _grpc_plugins(self):
        return {
            "cpp_plugin": {
                "target": "gRPC::grpc_cpp_plugin",
                "executable": "grpc_cpp_plugin",
            },
            "csharp_plugin": {
                "target": "gRPC::grpc_csharp_plugin",
                "executable": "grpc_csharp_plugin",
            },
            "node_plugin": {
                "target": "gRPC::grpc_node_plugin",
                "executable": "grpc_node_plugin",
            },
            "objective_c_plugin": {
                "target": "gRPC::grpc_objective_c_plugin",
                "executable": "grpc_objective_c_plugin",
            },
            "php_plugin": {
                "target": "gRPC::grpc_php_plugin",
                "executable": "grpc_php_plugin",
            },
            "python_plugin": {
                "target": "gRPC::grpc_python_plugin",
                "executable": "grpc_python_plugin",
            },
            "ruby_plugin": {
                "target": "gRPC::grpc_ruby_plugin",
                "executable": "grpc_ruby_plugin",
            },
        }

    def _create_executable_module_file(self, target, executable):
        # Copy our CMake module template file to package folder
        self.copy(self._grpc_plugin_template, dst=self._module_path,
                  src=os.path.join(self.source_folder, "cmake"))

        # Rename it
        dst_file = os.path.join(self.package_folder, self._module_path,
                                "{}.cmake".format(executable))
        tools.rename(os.path.join(self.package_folder, self._module_path,
                                  self._grpc_plugin_template),
                     dst_file)

        # Replace placeholders
        tools.replace_in_file(dst_file, "@target_name@", target)
        tools.replace_in_file(dst_file, "@executable_name@", executable)

        find_program_var = "{}_PROGRAM".format(executable.upper())
        tools.replace_in_file(dst_file, "@find_program_variable@", find_program_var)

        module_folder_depth = len(os.path.normpath(self._module_path).split(os.path.sep))
        rel_path = "".join(["../"] * module_folder_depth)
        tools.replace_in_file(dst_file, "@relative_path@", rel_path)

    @property
    def _module_path(self):
        return os.path.join("lib", "cmake", "conan_trick")

    @property
    def _grpc_components(self):
        def libm():
            return ["m"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def pthread():
            return ["pthread"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def crypt32():
            return ["crypt32"] if self.settings.os == "Windows" else []

        def ws2_32():
            return ["ws2_32"] if self.settings.os == "Windows" else []

        def wsock32():
            return ["wsock32"] if self.settings.os == "Windows" else []

        def corefoundation():
            return ["CoreFoundation"] if tools.is_apple_os(self.settings.os) else []

        components = {
            "address_sorting": {
                "lib": "address_sorting",
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
            },
            "gpr": {
                "lib": "gpr",
                "requires": [
                    "upb", "abseil::absl_base", "abseil::absl_memory",
                    "abseil::absl_status", "abseil::absl_str_format",
                    "abseil::absl_strings", "abseil::absl_synchronization",
                    "abseil::absl_time", "abseil::absl_optional",
                ],
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
            },
            "_grpc": {
                "lib": "grpc",
                "requires": [
                    "address_sorting", "gpr", "upb", "abseil::absl_bind_front",
                    "abseil::absl_flat_hash_map", "abseil::absl_inlined_vector",
                    "abseil::absl_statusor", "c-ares::cares", "openssl::crypto",
                    "openssl::ssl", "re2::re2", "zlib::zlib",
                ],
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
                "frameworks": corefoundation(),
            },
            "grpc++": {
                "lib": "grpc++",
                "requires": ["_grpc", "protobuf::libprotobuf"],
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
            },
            "grpc++_alts": {
                "lib": "grpc++_alts",
                "requires": ["grpc++", "protobuf::libprotobuf"],
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
            },
            "grpc++_error_details": {
                "lib": "grpc++_error_details",
                "requires": ["grpc++", "protobuf::libprotobuf"],
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
            },
            "upb": {
                "lib": "upb",
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
            },
            "grpc_plugin_support": {
                "lib": "grpc_plugin_support",
                "requires": ["protobuf::libprotoc", "protobuf::libprotobuf"],
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
            },
        }

        if not self.options.secure:
            components.update({
                "grpc_unsecure": {
                    "lib": "grpc_unsecure",
                    "requires": [
                        "address_sorting", "gpr", "upb", "abseil::absl_flat_hash_map",
                        "abseil::absl_inlined_vector", "abseil::absl_statusor",
                        "c-ares::cares", "re2::re2", "zlib::zlib",
                        "abseil::absl_random_random",
                    ],
                    "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
                    "frameworks": corefoundation(),
                },
                "grpc++_unsecure": {
                    "lib": "grpc++_unsecure",
                    "requires": ["grpc_unsecure", "protobuf::libprotobuf"],
                    "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
                },
            })

        if self.options.codegen:
            components.update({
                "grpc++_reflection": {
                    "lib": "grpc++_reflection",
                    "requires": ["grpc++", "protobuf::libprotobuf"],
                    "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
                },
                "grpcpp_channelz": {
                    "lib": "grpcpp_channelz",
                    "requires": ["grpc++", "protobuf::libprotobuf"],
                    "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
                },
            })

        return components

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gRPC")

        for component, values in self._grpc_components.items():
            target = values.get("lib")
            lib = values.get("lib")
            self.cpp_info.components[component].set_property("cmake_target_name", "gRPC::{}".format(target))
            # actually only gpr, grpc, grpc_unsecure, grpc++ and grpc++_unsecure should have a .pc file
            self.cpp_info.components[component].set_property("pkg_config_name", target)
            self.cpp_info.components[component].libs = [lib]
            self.cpp_info.components[component].requires = values.get("requires", [])
            self.cpp_info.components[component].system_libs = values.get("system_libs", [])
            self.cpp_info.components[component].frameworks = values.get("frameworks", [])

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components[component].names["cmake_find_package"] = target
            self.cpp_info.components[component].names["cmake_find_package_multi"] = target

        # Executable imported targets are added through custom CMake module files,
        # since conan generators don't know how to emulate these kind of targets.
        grpc_modules = []
        for plugin_option, values in self._grpc_plugins.items():
            if self.options.get_safe(plugin_option):
                grpc_module_filename = "{}.cmake".format(values["executable"])
                grpc_modules.append(os.path.join(self._module_path, grpc_module_filename))
        self.cpp_info.set_property("cmake_build_modules", grpc_modules)

        if any(self.options.get_safe(plugin_option) for plugin_option in self._grpc_plugins.keys()):
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "gRPC"
        self.cpp_info.names["cmake_find_package_multi"] = "gRPC"
        if grpc_modules:
            self.cpp_info.components["grpc_execs"].build_modules["cmake_find_package"] = grpc_modules
            self.cpp_info.components["grpc_execs"].build_modules["cmake_find_package_multi"] = grpc_modules
