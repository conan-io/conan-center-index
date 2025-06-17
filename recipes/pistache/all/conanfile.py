from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, replace_in_file, collect_libs
from conan.tools.build import check_min_cppstd
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.layout import basic_layout
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version

import os

required_conan_version = ">=2.0.9"

class PistacheConan(ConanFile):
    name = "pistache"
    description = "Pistache is a modern and elegant HTTP and REST framework for C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pistacheio/pistache"
    topics = ("http", "rest", "framework", "networking")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
        "with_libevent": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
        "with_libevent": True
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _supports_libevent(self):
        return Version(self.version) >= "0.4.25"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux" or not self._supports_libevent:
            del self.options.with_libevent

    def requirements(self):
        self.requires("rapidjson/cci.20230929")
        self.requires("date/3.0.1")
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.get_safe("with_libevent", True):
            self.requires("libevent/2.1.12")

    def validate(self):
        if self.settings.os != "Linux" and Version(self.version) < "0.4.25":
            raise ConanInvalidConfiguration(f"{self.ref} is only support on Linux.")
        if self.settings.compiler == "clang" and Version(self.version) < "0.4.25":
            raise ConanInvalidConfiguration(f"{self.ref}'s clang support is broken. See pistacheio/pistache#835.")
        
        if Version(self.version) == "0.4.25" and self.settings.os == "Windows":
            # See https://github.com/conan-io/conan-center-index/pull/26463#issuecomment-2962541819
            raise ConanInvalidConfiguration("Windows builds are broken - contributions welcome")

        check_min_cppstd(self, 17)


    def build_requirements(self):
        self.tool_requires("meson/[>=1.3.1 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["PISTACHE_USE_SSL"] = self.options.with_ssl
        tc.project_options["PISTACHE_BUILD_EXAMPLES"] = False
        tc.project_options["PISTACHE_BUILD_TESTS"] = False
        tc.project_options["PISTACHE_BUILD_DOCS"] = False
        if self._supports_libevent:
            tc.project_options["PISTACHE_FORCE_LIBEVENT"] = self.options.get_safe("with_libevent", True)
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                                "dependency('RapidJSON', fallback: ['rapidjson', 'rapidjson_dep'])",
                                "dependency('rapidjson', fallback: ['rapidjson', 'rapidjson_dep'])")
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
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
        if self.options.get_safe("with_libevent", True):
            self.cpp_info.components["libpistache"].requires.append("libevent::libevent")
        self.cpp_info.components["libpistache"].requires.append("date::date")
        if self.options.with_ssl:
            self.cpp_info.components["libpistache"].requires.append("openssl::openssl")
            self.cpp_info.components["libpistache"].defines = ["PISTACHE_USE_SSL=1"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libpistache"].system_libs = ["pthread", "m"]
