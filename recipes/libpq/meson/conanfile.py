from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain

import os

required_conan_version = ">=2.18.0"


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
        # False to keep in line with old versions,
        # but this is True by default in upstream
        "with_icu": False,
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

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "msvc":
            del self.options.with_readline

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
            self.requires("libxslt/[^1.1]")
        if self.options.get_safe("with_readline"):
            self.requires("readline/8.2")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings_build.os == "Windows":
            self.tool_requires("strawberryperl/5.32.1.1")
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        def feature(v):
            return "enabled" if v else "disabled"

        tc = MesonToolchain(self)
        tc.project_options["ssl"] = "openssl" if self.options.with_openssl else "none"
        tc.project_options["icu"] = feature(self.options.with_icu)
        # Why did the old version disable this explicitly?
        tc.project_options["zlib"] = feature(self.options.with_zlib)
        tc.project_options["zstd"] = feature(self.options.with_zstd)
        tc.project_options["libxml"] = feature(self.options.with_libxml2)
        tc.project_options["lz4"] = feature(self.options.with_lz4)
        tc.project_options["libxslt"] = feature(self.options.with_xslt)
        tc.project_options["readline"] = feature(self.options.get_safe("with_readline"))

        tc.project_options["ldap"] = "disabled"
        tc.project_options["tap_tests"] = "disabled"
        tc.project_options["plpython"] = "disabled"
        tc.project_options["docs"] = "disabled"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYRIGHT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

        # INFO: When building on Windows:
        # - MSVC + Static: produces .a files
        # - MSVC + Shared: produces .lib + .dll files
        # - MinGW + Static: produces .a files
        # - MinGW + Shared: produces .dll.a + .dll files
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"), excludes="*.dll.a")
        else:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
            rm(self, "*.lib", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll.a", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PostgreSQL")
        # INFO: Upstream libpq.pc is specific for the main library, not the whole package.
        self.cpp_info.set_property("pkg_config_name", "none")

        self.runenv_info.define_path("PostgreSQL_ROOT", self.package_folder)

        # INFO: Using Meson will install more libraries than when using Autotools.
        # We list only the libraries that are actually used by the main library.
        self.cpp_info.components["pq"].libs = ["pq"]
        self.cpp_info.components["pq"].set_property("pkg_config_name", "libpq")
        self.cpp_info.components["pq"].set_property("cmake_target_name", "PostgreSQL::PostgreSQL")

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
            self.cpp_info.components["pgport"].libs = ["pgport"]
            self.cpp_info.components["pq"].requires.append("pgport")
            self.cpp_info.components["pgport"].libs.append("pgport_shlib")

            self.cpp_info.components["pgfeutils"].libs = ["pgfeutils"]
            self.cpp_info.components["pq"].requires.append("pgfeutils")

            # pgcommon and pgcommon_shlib have duplicated symbols
            # pgcommon_shlib is used for libraries, pgcommon is used for executables
            # https://github.com/postgres/postgres/blob/REL_17_5/src/common/Makefile#L15
            self.cpp_info.components["pgcommon"].libs = ["pgcommon_shlib"]
            self.cpp_info.components["pq"].requires.append("pgcommon")
            self.cpp_info.components["pgcommon"].requires = ["pgport", "pgfeutils"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["pq"].system_libs = ["pthread", "m", "dl", "rt"]
            self.cpp_info.components["pgcommon"].system_libs = ["m"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["pq"].system_libs = ["ws2_32", "secur32", "advapi32", "shell32", "crypt32", "wldap32"]
            self.cpp_info.components["pgcommon"].system_libs = ["ws2_32"]
