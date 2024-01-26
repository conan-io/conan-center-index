import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building, valid_min_cppstd, check_min_cppstd
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2 || >=2.0.5"


class GrpcConan(ConanFile):
    name = "grpc"
    package_type = "library"
    description = "Google's RPC (remote procedure call) library and framework."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/grpc/grpc"
    topics = ("rpc",)

    settings = "os", "arch", "compiler", "build_type"

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

    @property
    def _grpc_plugin_template(self):
        return "grpc_plugin_template.cmake.in"

    @property
    def _cxxstd_required(self):
        return 14 if Version(self.version) >= "1.47" else 11

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    def export_sources(self):
        copy(self, "conan_cmake_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        copy(self, f"cmake/{self._grpc_plugin_template}", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.options["protobuf"].shared = True

            if cross_building(self):
                self.options["grpc"].shared = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # abseil is public. See https://github.com/conan-io/conan-center-index/pull/17284#issuecomment-1526082638
        if Version(self.version) < "1.47":
            if is_msvc(self):
                self.requires("abseil/20211102.0", transitive_headers=True, transitive_libs=True)
            else:
                self.requires("abseil/20220623.1", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("abseil/20230125.3", transitive_headers=True, transitive_libs=True)
        self.requires("c-ares/1.19.1")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("protobuf/3.21.12", transitive_headers=True, transitive_libs=True)
        self.requires("re2/20230301")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.settings.os in ["Linux", "FreeBSD"] and Version(self.version) >= "1.52":
            self.requires("libsystemd/255")

    def package_id(self):
        del self.info.options.secure

    def validate(self):
        check_min_vs(self, "190")
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported by Visual Studio")

        if Version(self.version) >= "1.47" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6":
            raise ConanInvalidConfiguration("GCC older than 6 is not supported")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._cxxstd_required)

        if self.options.shared and not self.dependencies.host["protobuf"].options.shared:
            raise ConanInvalidConfiguration(
                "If built as shared protobuf must be shared as well. "
                "Please, use `protobuf:shared=True`.",
            )

    def build_requirements(self):
        if not self._is_legacy_one_profile:
            self.tool_requires("protobuf/<host_version>")
        if cross_building(self):
            # when cross compiling we need pre compiled grpc plugins for protoc
            self.tool_requires(f"grpc/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # Set up environment so that we can run grpc-cpp-plugin at build time
        VirtualBuildEnv(self).generate()
        if self._is_legacy_one_profile:
            VirtualRunEnv(self).generate(scope="build")

        # This doesn't work yet as one would expect, because the install target builds everything
        # and we need the install target because of the generated CMake files
        #
        #   enable_mobile=False # Enables iOS and Android support
        #
        # cmake.definitions["CONAN_ENABLE_MOBILE"] = "ON" if self.options.csharp_ext else "OFF"
        tc = CMakeToolchain(self)

        tc.cache_variables["CMAKE_PROJECT_grpc_INCLUDE"] = os.path.join(self.source_folder, "conan_cmake_project_include.cmake")

        tc.cache_variables["gRPC_BUILD_CODEGEN"] = self.options.codegen
        tc.cache_variables["gRPC_BUILD_CSHARP_EXT"] = self.options.csharp_ext
        tc.cache_variables["gRPC_BUILD_TESTS"] = "OFF"

        # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
        tc.cache_variables["gRPC_INSTALL"] = True
        tc.cache_variables["gRPC_INSTALL_SHAREDIR"] = "res/grpc"

        # tell grpc to use the find_package versions
        tc.cache_variables["gRPC_ZLIB_PROVIDER"] = "package"
        tc.cache_variables["gRPC_CARES_PROVIDER"] = "package"
        tc.cache_variables["gRPC_RE2_PROVIDER"] = "package"
        tc.cache_variables["gRPC_SSL_PROVIDER"] = "package"
        tc.cache_variables["gRPC_PROTOBUF_PROVIDER"] = "package"
        tc.cache_variables["gRPC_ABSL_PROVIDER"] = "package"

        tc.cache_variables["gRPC_BUILD_GRPC_CPP_PLUGIN"] = self.options.cpp_plugin
        tc.cache_variables["gRPC_BUILD_GRPC_CSHARP_PLUGIN"] = self.options.csharp_plugin
        tc.cache_variables["gRPC_BUILD_GRPC_NODE_PLUGIN"] = self.options.node_plugin
        tc.cache_variables["gRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN"] = self.options.objective_c_plugin
        tc.cache_variables["gRPC_BUILD_GRPC_PHP_PLUGIN"] = self.options.php_plugin
        tc.cache_variables["gRPC_BUILD_GRPC_PYTHON_PLUGIN"] = self.options.python_plugin
        tc.cache_variables["gRPC_BUILD_GRPC_RUBY_PLUGIN"] = self.options.ruby_plugin

        # Consumed targets (abseil) via interface target_compiler_feature can propagate newer standards
        if not valid_min_cppstd(self, self._cxxstd_required):
            tc.cache_variables["CMAKE_CXX_STANDARD"] = self._cxxstd_required

        if is_apple_os(self):
            # workaround for: install TARGETS given no BUNDLE DESTINATION for MACOSX_BUNDLE executable
            tc.cache_variables["CMAKE_MACOSX_BUNDLE"] = False

        if is_msvc(self) and Version(self.version) >= "1.48":
            tc.cache_variables["CMAKE_SYSTEM_VERSION"] = "10.0.18362.0"

        tc.generate()

        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # On macOS if all the following are true:
        # - protoc from protobuf has shared library dependencies
        # - grpc_cpp_plugin has shared library deps (when crossbuilding)
        # - using `make` as the cmake generator
        # Make will run commands via `/bin/sh` which will strip all env vars that start with `DYLD*`
        # This workaround wraps the protoc command to be invoked by CMake with a modified environment
        settings_build = getattr(self, "settings_build", self.settings)
        if settings_build.os == "Macos":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "COMMAND ${_gRPC_PROTOBUF_PROTOC_EXECUTABLE}",
                            'COMMAND ${CMAKE_COMMAND} -E env "DYLD_LIBRARY_PATH=$ENV{DYLD_LIBRARY_PATH}" ${_gRPC_PROTOBUF_PROTOC_EXECUTABLE}')
    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

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
        module_abs_path = os.path.join(self.package_folder, self._module_path)

        # Copy our CMake module template file to package folder
        copy(self, self._grpc_plugin_template, src=os.path.join(self.source_folder, "cmake"), dst=module_abs_path)

        # Rename it
        dst_file = os.path.join(module_abs_path, f"{executable}.cmake")
        rename(self, os.path.join(module_abs_path, self._grpc_plugin_template), dst_file)

        # Replace placeholders
        replace_in_file(self, dst_file, "@target_name@", target)
        replace_in_file(self, dst_file, "@executable_name@", executable)

        find_program_var = "{}_PROGRAM".format(executable.upper())
        replace_in_file(self, dst_file, "@find_program_variable@", find_program_var)

        module_folder_depth = len(os.path.normpath(self._module_path).split(os.path.sep))
        rel_path = "".join(["../"] * module_folder_depth)
        replace_in_file(self, dst_file, "@relative_path@", rel_path)

    @property
    def _module_path(self):
        return os.path.join("lib", "cmake", "conan_trick")

    @property
    def _grpc_components(self):

        def libsystemd():
            return ["libsystemd::libsystemd"] if self.settings.os in ["Linux", "FreeBSD"] and Version(self.version) >= "1.52" else []

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
            return ["CoreFoundation"] if is_apple_os(self) else []

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
                    "abseil::absl_flags"
                ] + libsystemd(),
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
            },
            "_grpc": {
                "lib": "grpc",
                "requires": [
                    "address_sorting", "gpr", "upb", "abseil::absl_bind_front",
                    "abseil::absl_flat_hash_map", "abseil::absl_inlined_vector",
                    "abseil::absl_statusor", "abseil::absl_random_random",
                    "c-ares::cares", "openssl::crypto",
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
        self.cpp_info.resdirs = ["res"]
        ssl_roots_file_path = os.path.join(self.package_folder, "res", "grpc", "roots.pem")
        self.runenv_info.define_path("GRPC_DEFAULT_SSL_ROOTS_FILE_PATH", ssl_roots_file_path)

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

        # TODO: to remove once conan v1 not supported anymore
        self.cpp_info.names["cmake_find_package"] = "gRPC"
        self.cpp_info.names["cmake_find_package_multi"] = "gRPC"
        self.env_info.GRPC_DEFAULT_SSL_ROOTS_FILE_PATH = ssl_roots_file_path
        if grpc_modules:
            self.cpp_info.components["grpc_execs"].build_modules["cmake_find_package"] = grpc_modules
            self.cpp_info.components["grpc_execs"].build_modules["cmake_find_package_multi"] = grpc_modules
        if any(self.options.get_safe(plugin_option) for plugin_option in self._grpc_plugins.keys()):
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
