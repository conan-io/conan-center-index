import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, replace_in_file, rmdir, rm
from conan.tools.microsoft import check_min_vs
from conan.tools.scm import Version

required_conan_version = ">=2"


class IceoryxConan(ConanFile):
    name = "iceoryx"
    description = "Eclipse iceoryx - true zero-copy inter-process-communication"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://iceoryx.io/"
    topics = ("Shared Memory", "IPC", "ROS", "Middleware")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "toml_config": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "toml_config": True,
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared
            self.package_type = "static-library"

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.toml_config:
            self.requires("cpptoml/0.1.1", transitive_headers=True)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("acl/2.3.1", transitive_headers=True)

    def validate(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)

        check_min_cppstd(self, 17 if compiler == "msvc" else 14)

        check_min_vs(self, 192)
        if compiler == "gcc":
            if version < "6":
                raise ConanInvalidConfiguration("Using Iceoryx with gcc requires gcc 6 or higher.")
            if version < "9" and compiler.get_safe("libcxx") == "libstdc++":
                raise ConanInvalidConfiguration("gcc < 9 with libstdc++ not supported")
            if version == "6":
                self.output.warning(
                    "Iceoryx package is compiled with gcc 6, it is recommended to use 7 or higher"
                )
                self.output.warning("GCC 6 will build with warnings.")
        elif compiler == "clang":
            if compiler.get_safe("libcxx") == "libstdc++":
                raise ConanInvalidConfiguration("clang with libstdc++ not supported")
            if (
                version == "7.0"
                and compiler.get_safe("libcxx") == "libc++"
                and self.options.get_safe("shared")
                and self.settings.build_type == "Debug"
            ):
                raise ConanInvalidConfiguration("shared Debug with clang 7.0 and libc++ not supported")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["TOML_CONFIG"] = self.options.toml_config
        tc.cache_variables["DOWNLOAD_TOML_LIB"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.set_property("cpptoml", "cmake_target_name", "cpptoml")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        hoofs_dir = os.path.join(self.source_folder, "iceoryx_hoofs")

        # Use acl::acl target, since plain acl fails to link
        replace_in_file(self, os.path.join(hoofs_dir, "CMakeLists.txt"), " acl", " acl::acl")

        # Honor fPIC option
        cmakelists_list = [
            os.path.join(self.source_folder, "iceoryx_dds", "CMakeLists.txt"),
            os.path.join(self.source_folder, "iceoryx_posh", "CMakeLists.txt"),
            os.path.join(self.source_folder, "tools", "introspection", "CMakeLists.txt"),
            os.path.join(hoofs_dir, "CMakeLists.txt"),
            os.path.join(self.source_folder, "iceoryx_binding_c", "CMakeLists.txt"),
            os.path.join(hoofs_dir, "platform", "CMakeLists.txt"),
        ]
        for cmakelists in cmakelists_list:
            replace_in_file(self, cmakelists, "POSITION_INDEPENDENT_CODE ON", "")

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.path.pardir))
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, ".clang-tidy", os.path.join(self.package_folder, "include"), recursive=True)
        if self.options.toml_config:
            mkdir(self, os.path.join(self.package_folder, "res"))
            rename(self, os.path.join(self.package_folder, "etc", "roudi_config_example.toml"),
                         os.path.join(self.package_folder, "res", "roudi_config.toml"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        # bring to default package structure
        include_paths = ["iceoryx_binding_c", "iceoryx_hoofs", "iceoryx_posh", "iceoryx_versions.hpp"]
        for include_path in include_paths:
            rename(self, os.path.join(self.package_folder, "include", "iceoryx", f"v{self.version}", include_path),
                         os.path.join(self.package_folder, "include", include_path))

    @property
    def _iceoryx_components(self):
        def pthread():
            return ["pthread"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def rt():
            return ["rt"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def atomic():
            return ["atomic"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def acl():
            return ["acl::acl"] if self.settings.os in ["Linux", "FreeBSD"] else []

        def cpptoml():
            return ["cpptoml::cpptoml"] if self.options.toml_config else []

        def libcxx():
            libcxx = stdcpp_library(self)
            return [libcxx] if libcxx and not self.options.shared else []

        return {
            "2.0.0": {
                "iceoryx_platform": {
                    "target": "iceoryx_hoofs::iceoryx_platform",
                    "system_libs": pthread() + rt(),
                    "requires": [],
                    "includeDir": False,
                },
                "iceoryx_hoofs": {
                    "target": "iceoryx_hoofs::iceoryx_hoofs",
                    "system_libs": pthread() + rt() + atomic(),
                    "requires": ["iceoryx_platform"] + acl(),
                    "includeDir": True,
                },
                "iceoryx_posh": {
                    "target": "iceoryx_posh::iceoryx_posh",
                    "system_libs": pthread() + rt(),
                    "requires": ["iceoryx_hoofs"],
                    "includeDir": True,
                },
                "iceoryx_posh_roudi": {
                    "target": "iceoryx_posh::iceoryx_posh_roudi",
                    "system_libs": pthread(),
                    "requires": ["iceoryx_hoofs", "iceoryx_posh"] + cpptoml(),
                    "includeDir": False,
                },
                "iceoryx_posh_gateway": {
                    "target": "iceoryx_posh::iceoryx_posh_gateway",
                    "system_libs": pthread(),
                    "requires": ["iceoryx_hoofs", "iceoryx_posh"],
                    "includeDir": False,
                },
                "iceoryx_posh_config": {
                    "target": "iceoryx_posh::iceoryx_posh_config",
                    "system_libs": pthread(),
                    "requires": ["iceoryx_posh_roudi", "iceoryx_hoofs", "iceoryx_posh"],
                    "includeDir": False,
                },
                "iceoryx_binding_c": {
                    "target": "iceoryx_binding_c::iceoryx_binding_c",
                    "system_libs": pthread() + libcxx(),
                    "requires": ["iceoryx_hoofs", "iceoryx_posh"],
                    "includeDir": True,
                },
            },
        }

    def package_info(self):
        # FIXME: We should provide 3 CMake config files:
        #        iceoryx_utilsConfig.cmake, iceoryx_poshConfig.cmake and iceoryx_binding_cConfig.cmake
        #        It's not possible yet, see https://github.com/conan-io/conan/issues/9000
        self.cpp_info.set_property("cmake_file_name", "iceoryx")

        def _register_components(components):
            for lib_name, values in components.items():
                cmake_target = values.get("target", [])
                system_libs = values.get("system_libs", [])
                requires = values.get("requires", [])
                self.cpp_info.components[lib_name].set_property("cmake_target_name", cmake_target)
                self.cpp_info.components[lib_name].libs = [lib_name]
                self.cpp_info.components[lib_name].system_libs = system_libs
                self.cpp_info.components[lib_name].requires = requires

        _register_components(self._iceoryx_components["2.0.0"])
