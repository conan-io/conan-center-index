import os
import yaml

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
    description = "Google's RPC (remote procedure call) library and framework."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/grpc/grpc"
    topics = ("rpc",)

    package_type = "library"
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
        "secure": [True, False],
        "with_libsystemd": [True, False]
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
        "with_libsystemd": True
    }

    short_paths = True
    _target_info = None

    @property
    def _grpc_plugin_template(self):
        return "grpc_plugin_template.cmake.in"

    @property
    def _cxxstd_required(self):
        return 14 if Version(self.version) >= "1.47" else 11

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    @property
    def _supports_libsystemd(self):
        return self.settings.os in ["Linux", "FreeBSD"] and Version(self.version) >= "1.52"

    def export(self):
        copy(self, f"target_info/grpc_{self.version}.yml", src=self.recipe_folder, dst=self.export_folder)

    def export_sources(self):
        copy(self, "conan_cmake_project_include.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        copy(self, f"cmake/{self._grpc_plugin_template}", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._supports_libsystemd:
            del self.options.with_libsystemd

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
        if Version(self.version) >= "1.62.0":
            self.requires("protobuf/5.27.0", transitive_headers=True)
            self.requires("abseil/[>=20240116.1 <20240117.0]", transitive_headers=True)
        else:
            self.requires("abseil/[>=20230125.3 <=20230802.1]", transitive_headers=True)
            self.requires("protobuf/3.21.12", transitive_headers=True)
        self.requires("c-ares/[>=1.19.1 <2]")
        self.requires("openssl/[>=1.1 <4]")
        self.requires("re2/20230301")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.get_safe("with_libsystemd"):
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

        if self._supports_libsystemd:
            tc.cache_variables["gRPC_USE_SYSTEMD"] = self.options.with_libsystemd
        
        if Version(self.version) >= "1.62.0":
            tc.cache_variables["gRPC_DOWNLOAD_ARCHIVES"] = False

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
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        settings_build = getattr(self, "settings_build", self.settings)
        if settings_build.os == "Macos":
            replace_in_file(self, cmakelists,
                            "COMMAND ${_gRPC_PROTOBUF_PROTOC_EXECUTABLE}",
                            'COMMAND ${CMAKE_COMMAND} -E env "DYLD_LIBRARY_PATH=$ENV{DYLD_LIBRARY_PATH}" ${_gRPC_PROTOBUF_PROTOC_EXECUTABLE}')
        elif not cross_building(self) and settings_build.os == "Linux":
            # we are not cross-building, but protobuf or abseil may be shared
            # so we need to set LD_LIBRARY_PATH to find them
            # Note: if protobuf used RPATH instead of RUNPATH this is not needed
            replace_in_file(self, cmakelists,
                            "COMMAND ${_gRPC_PROTOBUF_PROTOC_EXECUTABLE}",
                            'COMMAND ${CMAKE_COMMAND} -E env "LD_LIBRARY_PATH=$<JOIN:${CMAKE_LIBRARY_PATH},:>:$ENV{LD_LIBRARY_PATH}" ${_gRPC_PROTOBUF_PROTOC_EXECUTABLE}')
        if self.settings.os == "Macos" and Version(self.version) >= "1.64":
            # See https://github.com/grpc/grpc/issues/36654#issuecomment-2228569158
            replace_in_file(self, cmakelists, "target_compile_features(upb_textformat_lib PUBLIC cxx_std_14)",
            """target_compile_features(upb_textformat_lib PUBLIC cxx_std_14)
            target_link_options(upb_textformat_lib PRIVATE -Wl,-undefined,dynamic_lookup)
            target_link_options(upb_json_lib PRIVATE -Wl,-undefined,dynamic_lookup)
            """)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def target_info(self):
        if self._target_info:
            return self._target_info
        target_info_file = os.path.join(self.recipe_folder, "target_info", f"grpc_{self.version}.yml")
        with open(target_info_file) as f:
            self._target_info = yaml.safe_load(f)
        return self._target_info

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # Create one custom module file per executable in order to emulate
        # CMake executables imported targets of grpc plugins.
        for plugin_info in self.target_info["grpc_plugins"]:
            target = plugin_info["target"]
            executable = plugin_info["executable"]
            option_name = executable.replace("grpc_", "")
            if self.options.get_safe(option_name):
                self._create_executable_module_file(target, executable)

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
            return ["libsystemd::libsystemd"] if self._supports_libsystemd and self.options.with_libsystemd else []

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

        targets = self.target_info['grpc_targets']
        components = {}
        for target in targets:
            if self.options.secure and target['name'] in ["grpc_unsecure", "grpc++_unsecure"]:
                continue
            if not self.options.codegen and target['name'] in ["grpc++_reflection", "grpcpp_channelz"]:
                continue
            components[target['name']] = {
                "lib": target['lib'],
                "requires": target.get('requires', []) + libsystemd(),
                "system_libs": libm() + pthread() + crypt32() + ws2_32() + wsock32(),
                "frameworks": target.get('frameworks', []),
            }

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
        for plugin_info in self.target_info["grpc_plugins"]:
            executable = plugin_info["executable"]
            option_name = executable.replace("grpc_", "")
            if self.options.get_safe(option_name):
                grpc_module_filename = "{}.cmake".format(executable)
                grpc_modules.append(os.path.join(self._module_path, grpc_module_filename))
        self.cpp_info.set_property("cmake_build_modules", grpc_modules)

        # TODO: to remove once conan v1 not supported anymore
        self.cpp_info.names["cmake_find_package"] = "gRPC"
        self.cpp_info.names["cmake_find_package_multi"] = "gRPC"
        self.env_info.GRPC_DEFAULT_SSL_ROOTS_FILE_PATH = ssl_roots_file_path
        if grpc_modules:
            self.cpp_info.components["grpc_execs"].build_modules["cmake_find_package"] = grpc_modules
            self.cpp_info.components["grpc_execs"].build_modules["cmake_find_package_multi"] = grpc_modules
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
