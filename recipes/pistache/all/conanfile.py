from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.layout import basic_layout
from conan.tools.gnu import PkgConfigDeps

import os

required_conan_version = ">=1.53.0"

class PistacheConan(ConanFile):
    name = "pistache"
    license = "Apache-2.0"
    homepage = "https://github.com/pistacheio/pistache"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("http", "rest", "framework", "networking")
    description = "Pistache is a modern and elegant HTTP and REST framework for C++"

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
            self.requires("openssl/1.1.1s")
        if self.version != "cci.20201127":
            self.requires("date/3.0.1")

    def validate(self):
        compilers = {
            "gcc": "7",
            "clang": "6",
        }
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(f"{self.ref} is only support on Linux.")

        if self.settings.compiler == "clang":
            raise ConanInvalidConfiguration("Clang support is broken. See pistacheio/pistache#835.")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
        minimum_compiler = compilers.get(str(self.settings.compiler))
        if minimum_compiler:
            if Version(self.settings.compiler.version) < minimum_compiler:
                raise ConanInvalidConfiguration(f"{self.ref} requires c++17, which your compiler does not support.")
        else:
            self.output.warn(f"{self.ref} requires c++17, but this compiler is unknown to this recipe. Assuming your compiler supports c++17.")

    def build_requirements(self):
        if self.version != "cci.20201127":
            self.tool_requires("meson/1.0.0")
            if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
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
            tc = MesonToolchain(self)
            tc.project_options["PISTACHE_USE_SSL"] = self.options.with_ssl
            tc.project_options["PISTACHE_BUILD_EXAMPLES"] = False
            tc.project_options["PISTACHE_BUILD_TESTS"] = False
            tc.project_options["PISTACHE_BUILD_DOCS"] = False
            tc.generate()

            tc = PkgConfigDeps(self)
            tc.generate()

            env = VirtualBuildEnv(self)
            env.generate(scope="build")

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
        else:
            meson = Meson(self)
            meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        # TODO: Pistache does not use namespace
        # TODO: Pistache variables are CamelCase e.g Pistache_BUILD_DIRS
        self.cpp_info.set_property("cmake_file_name", "Pistache")
        self.cpp_info.set_property("cmake_target_name", "Pistache::Pistache")
        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "libpistache")

        self.cpp_info.components["libpistache"].libs = collect_libs(self)
        self.cpp_info.components["libpistache"].requires = ["rapidjson::rapidjson"]
        if self.options.with_ssl:
            self.cpp_info.components["libpistache"].requires.append("openssl::openssl")
            self.cpp_info.components["libpistache"].defines = ["PISTACHE_USE_SSL=1"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libpistache"].system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Pistache"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Pistache"
        self.cpp_info.names["cmake_find_package"] = "Pistache"
        self.cpp_info.names["cmake_find_package_multi"] = "Pistache"
        self.cpp_info.names["pkg_config"] = "libpistache"
        suffix = "_{}".format("shared" if self.options.shared else "static")
        self.cpp_info.components["libpistache"].names["cmake_find_package"] = "pistache" + suffix
        self.cpp_info.components["libpistache"].names["cmake_find_package_multi"] = "pistache" + suffix
