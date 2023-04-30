from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import (
    apply_conandata_patches, collect_libs, copy, export_conandata_patches, get,
    replace_in_file, rmdir, save
)
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.layout import basic_layout
from conan.tools.gnu import PkgConfigDeps

import os
import textwrap

required_conan_version = ">=1.53.0"

class PistacheConan(ConanFile):
    name = "pistache"
    license = "Apache-2.0"
    homepage = "https://github.com/pistacheio/pistache"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("http", "rest", "framework", "networking")
    description = "Pistache is a modern and elegant HTTP and REST framework for C++"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
    }

    @property
    def _min_cppstd(self):
        return "14" if self.version == "cci.20201127" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        if self.version == "cci.20201127":
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("rapidjson/cci.20220822")
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.version != "cci.20201127":
            self.requires("date/3.0.1")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is only supported on Linux.")

        if self.settings.compiler == "clang":
            raise ConanInvalidConfiguration("Clang support is broken. See pistacheio/pistache#835.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def build_requirements(self):
        if self.version != "cci.20201127":
            self.tool_requires("meson/1.1.0")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.version == "cci.20201127":
            tc = CMakeToolchain(self)
            tc.variables["PISTACHE_ENABLE_NETWORK_TESTS"] = False
            tc.variables["PISTACHE_USE_SSL"] = self.options.with_ssl
            # pistache requires explicit value for fPIC
            tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
            tc.generate()

            tc = CMakeDeps(self)
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()

            tc = MesonToolchain(self)
            tc.project_options["PISTACHE_USE_SSL"] = self.options.with_ssl
            tc.project_options["PISTACHE_BUILD_EXAMPLES"] = False
            tc.project_options["PISTACHE_BUILD_TESTS"] = False
            tc.project_options["PISTACHE_BUILD_DOCS"] = False
            tc.generate()

            tc = PkgConfigDeps(self)
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if self.version != "cci.20201127":
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                                    "dependency('RapidJSON', fallback: ['rapidjson', 'rapidjson_dep']),",
                                    "dependency('rapidjson', fallback: ['rapidjson', 'rapidjson_dep']),")

        if self.version == "cci.20201127":
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            meson = Meson(self)
            meson.configure()
            meson.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.version == "cci.20201127":
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        else:
            meson = Meson(self)
            meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._cmake_target: "Pistache::Pistache"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _cmake_target(self):
        return "pistache_shared" if self.options.shared else "pistache_static"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Pistache")
        self.cpp_info.set_property("cmake_target_name", self._cmake_target)
        # not official but avoid to break previous target name expectations of this recipe
        self.cpp_info.set_property("cmake_target_aliases", ["Pistache::Pistache"])
        self.cpp_info.set_property("pkg_config_name", "libpistache")
        self.cpp_info.libs = collect_libs(self)
        if self.options.with_ssl:
            self.cpp_info.defines = ["PISTACHE_USE_SSL=1"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Pistache"
        self.cpp_info.names["cmake_find_package_multi"] = "Pistache"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
