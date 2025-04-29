from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, collect_libs
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.4"


class LibpqConan(ConanFile):
    name = "libpq"
    description = "The library used by all the standard PostgreSQL tools."
    topics = ("postgresql", "database", "db")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.postgresql.org/docs/current/static/libpq.html"
    license = "PostgreSQL"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_icu": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
        "with_libxml2": [True, False],
        "with_lz4": [True, False],
        "with_xslt": [True, False],
        "with_readline": [True, False],
        "disable_rpath": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": True,
        "with_icu": True,
        "with_zlib": True,
        "with_zstd": True,
        "with_libxml2": True,
        "with_lz4": True,
        "with_xslt": True,
        "with_readline": True,
        "disable_rpath": False,
    }

    languages = "C"
    implements = ["auto_shared_fpic"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "msvc":
            del self.options.with_readline

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_icu:
            self.requires("icu/75.1")
        if self.options.with_libxml2:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.with_zstd:
            self.requires("zstd/[>=1.5 <1.6]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_xslt:
            self.requires("libxslt/1.1.42")
        if self.options.get_safe("with_readline"):
            self.requires("readline/8.2")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")
        if self.settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.25")
            # self.win_bash = True
            # if not self.conf.get("tools.microsoft.bash:path", check_type=str):
            #     self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        def feature(v): return "enabled" if v else "disabled"

        tc = MesonToolchain(self)
        tc.project_options["ssl"] = "openssl" if self.options.with_openssl else "disabled"
        tc.project_options["icu"] = feature(self.options.with_icu)
        # Why did the old version disable this explicitly?
        tc.project_options["zlib"] = feature(self.options.with_zlib)
        tc.project_options["zstd"] = feature(self.options.with_zstd)
        tc.project_options["libxml"] = feature(self.options.with_libxml2)
        tc.project_options["lz4"] = feature(self.options.with_lz4)
        tc.project_options["libxslt"] = feature(self.options.with_xslt)
        tc.project_options["readline"] = feature(self.options.get_safe("with_readline"))

        tc.project_options["tap_tests"] = "disabled"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PostgreSQL")
        self.cpp_info.set_property("cmake_target_name", "PostgreSQL::PostgreSQL")
        self.cpp_info.set_property("pkg_config_name", "libpq")

        self.runenv_info.define_path("PostgreSQL_ROOT", self.package_folder)

        self.cpp_info.components["pq"].libs = [f"{'lib' if is_msvc(self) else ''}pq"]

        if self.options.with_openssl:
            self.cpp_info.components["pq"].requires.append("openssl::openssl")
        if self.options.with_icu:
            self.cpp_info.components["pq"].requires.append("icu::icu")
        if self.options.with_zlib:
            self.cpp_info.components["pq"].requires.append("zlib::zlib")
        if self.options.with_zstd:
            self.cpp_info.components["pq"].requires.append("zstd::zstd")
        if self.options.with_libxml2:
            self.cpp_info.components["pq"].requires.append("libxml2::libxml2")
        if self.options.with_lz4:
            self.cpp_info.components["pq"].requires.append("lz4::lz4")
        if self.options.with_xslt:
            self.cpp_info.components["pq"].requires.append("libxslt::libxslt")
        if self.options.get_safe("with_readline"):
            self.cpp_info.components["pq"].requires.append("readline::readline")

        if not self.options.shared:
            if is_msvc(self):
                self.cpp_info.components["pgport"].libs = ["libpgport"]
                self.cpp_info.components["pq"].requires.append("pgport")
                self.cpp_info.components["pgcommon"].libs = ["libpgcommon"]
                self.cpp_info.components["pq"].requires.append("pgcommon")
            else:
                self.cpp_info.components["pgcommon"].libs = ["pgcommon"]
                self.cpp_info.components["pq"].requires.append("pgcommon")
                self.cpp_info.components["pgcommon"].libs.append("pgcommon_shlib")
                self.cpp_info.components["pgport"].libs = ["pgport", "pgport_shlib"]
                if self.settings.os == "Windows":
                    self.cpp_info.components["pgport"].system_libs = ["ws2_32"]
                self.cpp_info.components["pgcommon"].requires.append("pgport")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["pq"].system_libs = ["pthread"]
            self.cpp_info.components["pgcommon"].system_libs = ["m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["pq"].system_libs = ["ws2_32", "secur32", "advapi32", "shell32", "crypt32", "wldap32"]

