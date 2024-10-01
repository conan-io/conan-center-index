import glob
import os
from pathlib import Path

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.54.0"


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
        "build_psql": [True, False],
        "build_server": [True, False],
        "build_tools": [True, False],
        "disable_rpath": [True, False],
        "with_bonjour": [True, False],
        "with_gssapi": [True, False],
        "with_icu": [True, False],
        "with_ldap": [True, False],
        "with_libxml": [True, False],
        "with_libxslt": [True, False],
        "with_lz4": [True, False],
        "with_nls": [True, False],
        "with_openssl": [True, False],
        "with_pam": [True, False],
        "with_readline": ["readline", "editline", False],
        "with_selinux": [True, False],
        "with_systemd": [True, False],
        "with_uuid": [True, False],
        "with_zlib": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_psql": False,
        "build_server": False,
        "build_tools": False,
        "disable_rpath": False,
        # libpq dependencies
        "with_gssapi": False,
        "with_ldap": False,
        "with_openssl": True,
        "with_zlib": True,
        "with_zstd": True,
        # module dependencies
        "with_libxml": False,
        "with_libxslt": False,
        "with_nls": False,
        "with_selinux": False,
        "with_uuid": False,
        # psql executable dependencies
        "with_readline": "editline",
        # postgres server executable dependencies
        "with_bonjour": True,
        "with_icu": True,
        "with_lz4": True,
        "with_pam": True,
        "with_systemd": True,
    }
    options_description = {
        "build_psql": "Build the psql command line tool",
        "build_server": "Build the PostgreSQL server executable",
        "build_tools": "Build all other tools",
        "with_bonjour": "Bonjour support",
        "with_gssapi": "GSSAPI support",
        "with_icu": "ICU support",
        "with_ldap": "LDAP support",
        "with_libxml": "XML support",
        "with_libxslt": "XSLT support in contrib/xml2",
        "with_lz4": "LZ4 support",
        "with_nls": "Native language support",
        "with_openssl": "Use OpenSSL for SSL/TLS support",
        "with_pam": "PAM support",
        "with_readline": "Use GNU Readline or BSD Libedit for editing in the psql command line tool",
        "with_selinux": "SELinux support",
        "with_systemd": "systemd support",
        "with_uuid": "Use LIB for contrib/uuid-ossp support",
        "with_zlib": "Enable zlib",
        "with_zstd": "Enable zstd",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.disable_rpath
        if not is_apple_os(self):
            # TODO: add mDNS support on other platforms using Avahi or mDNSResponder
            del self.options.with_bonjour
        if self.settings.os != "Linux":
            del self.options.with_selinux
            del self.options.with_systemd
            del self.options.with_pam

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if not self.options.build_psql:
            self.options.rm_safe("with_readline")
        if not self.options.build_server:
            self.options.rm_safe("with_bonjour")
            self.options.rm_safe("with_icu")
            self.options.rm_safe("with_lz4")
            self.options.rm_safe("with_pam")
            self.options.rm_safe("with_systemd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_gssapi:
            self.requires("krb5/1.21.2")
        if self.options.get_safe("with_icu"):
            self.requires("icu/75.1")
        if self.options.with_ldap:
            self.requires("openldap/2.6.7")
        if self.options.with_libxml:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.with_libxslt:
            self.requires("libxslt/1.1.42")
        if self.options.get_safe("with_lz4"):
            self.requires("lz4/1.9.4")
        if self.options.with_nls:
            self.requires("libgettext/0.22")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.get_safe("with_pam"):
            self.requires("linux-pam/1.6.1")
        if self.options.get_safe("with_readline") == "readline":
            self.requires("readline/8.2")
        elif self.options.get_safe("with_readline") == "editline":
            self.requires("editline/3.1")
        if self.options.get_safe("with_selinux"):
            self.requires("libselinux/3.6")
        if self.options.get_safe("with_systemd"):
            self.requires("libsystemd/255.10")
        if self.options.with_uuid:
            self.requires("util-linux-libuuid/2.39.2")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_zstd:
            self.requires("zstd/[~1.5]")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self._settings_build.os == "Windows":
            self.tool_requires("winflexbison/2.5.24")
            self.tool_requires("strawberryperl/5.32.1.1")
        else:
            self.tool_requires("flex/2.6.4")
            self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        feature = lambda option: "enabled" if option else "disabled"
        true_false = lambda option: "true" if option else "false"

        tc = MesonToolchain(self)
        tc.project_options["rpath"] = true_false(not self.options.get_safe("disable_rpath"))
        tc.project_options["bonjour"] = feature(self.options.get_safe("with_bonjour"))
        tc.project_options["bsd_auth"] = "disabled"
        tc.project_options["docs"] = "disabled"
        tc.project_options["dtrace"] = "disabled"
        tc.project_options["gssapi"] = feature(self.options.with_gssapi)
        tc.project_options["icu"] = feature(self.options.get_safe("with_icu"))
        tc.project_options["ldap"] = feature(self.options.with_ldap)
        tc.project_options["libxml"] = feature(self.options.with_libxml)
        tc.project_options["libxslt"] = feature(self.options.with_libxslt)
        tc.project_options["llvm"] = "disabled"
        tc.project_options["lz4"] = feature(self.options.get_safe("with_lz4"))
        tc.project_options["nls"] = feature(self.options.with_nls)
        tc.project_options["pam"] = feature(self.options.get_safe("with_pam"))
        tc.project_options["plperl"] = "disabled"
        tc.project_options["plpython"] = "disabled"
        tc.project_options["pltcl"] = "disabled"
        tc.project_options["readline"] = feature(self.options.get_safe("with_readline"))
        tc.project_options["libedit_preferred"] = true_false(self.options.get_safe("with_readline") == "editline")
        tc.project_options["selinux"] = feature(self.options.get_safe("with_selinux"))
        tc.project_options["ssl"] = "openssl" if self.options.with_openssl else "none"
        tc.project_options["systemd"] = feature(self.options.get_safe("with_systemd"))
        tc.project_options["uuid"] = "e2fs" if self.options.with_uuid else "none"
        tc.project_options["zlib"] = feature(self.options.with_zlib)
        tc.project_options["zstd"] = feature(self.options.with_zstd)
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _remove_unused_libraries_from_package(self):
        bin_folder = os.path.join(self.package_folder, "bin")
        lib_folder = os.path.join(self.package_folder, "lib")
        rm(self, "*.dll", lib_folder)
        if self.options.shared:
            for lib in glob.glob(os.path.join(lib_folder, "*.a")):
                if not (self.settings.os == "Windows" and os.path.basename(lib) == "libpq.dll.a"):
                    os.remove(lib)
        else:
            rm(self, "*.dll", bin_folder)
            rm(self, "*.dll.a", lib_folder)
            rm(self, "*.so*", lib_folder)
            rm(self, "*.dylib", lib_folder)
        if self.settings.os == "Windows":
            # Produced by building postgres.exe and only on Windows.
            # Does not have a corresponding .pc file.
            rm(self, "postgres.lib", lib_folder)

    def _remove_executables(self):
        # There's no way to disable building of the executables as of v17.0,
        # so simply remove them from the package instead to keep the size down.
        for path in Path(self.package_folder, "bin").iterdir():
            if path.name.endswith(".dll"):
                continue
            if path.stem == "postgres" and not self.options.build_server:
                path.unlink()
            elif path.stem == "psql" and not self.options.build_psql:
                path.unlink()
            elif not self.options.build_tools:
                path.unlink()

    def package(self):
        copy(self, "COPYRIGHT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        copy(self, "*.h",
             os.path.join(self.source_folder, "src", "include", "catalog"),
             os.path.join(self.package_folder, "include", "catalog"))
        copy(self, "*.h",
             os.path.join(self.build_folder, "src", "backend", "catalog"),
             os.path.join(self.package_folder, "include", "catalog"))
        self._remove_unused_libraries_from_package()
        self._remove_executables()
        fix_apple_shared_install_name(self)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        os.rename(os.path.join(self.package_folder, "share"),
                  os.path.join(self.package_folder, "res"))

    def _libname(self, name):
        return "lib" + name if is_msvc(self) else name

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "PostgreSQL")
        self.cpp_info.set_property("pkg_config_name", "libpq-do-not-use")

        self.cpp_info.components["pq"].set_property("pkg_config_name", "libpq")
        self.cpp_info.components["pq"].set_property("cmake_target_name", "PostgreSQL::PostgreSQL")
        self.cpp_info.components["pq"].libs = [self._libname("pq")]
        self.cpp_info.components["pq"].libdirs.append(os.path.join("lib", "postgresql"))
        self.cpp_info.components["pq"].resdirs = ["res"]
        self.cpp_info.components["pq"].requires = ["_common"]
        if self.options.with_gssapi:
            self.cpp_info.components["pq"].requires.append("krb5::krb5-gssapi")
        if self.options.with_ldap:
            self.cpp_info.components["pq"].requires.append("openldap::openldap")

        # Private frontend static libs and dependencies
        self.cpp_info.components["_common"].libs = []
        if not self.options.shared:
            self.cpp_info.components["_common"].libs.extend([
                self._libname("pgfeutils"),
                self._libname("pgcommon_shlib"),
                self._libname("pgport_shlib"),
            ])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_common"].system_libs.extend(["pthread", "m"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["_common"].system_libs.extend(["ws2_32", "secur32"])
        if self.options.with_zlib:
            self.cpp_info.components["_common"].requires.append("zlib::zlib")
        if self.options.with_zstd:
            self.cpp_info.components["_common"].requires.append("zstd::zstd")
        if self.options.with_openssl:
            self.cpp_info.components["_common"].requires.append("openssl::openssl")

        self.cpp_info.components["pgtypes"].set_property("pkg_config_name", "libpgtypes")
        self.cpp_info.components["pgtypes"].libs = [self._libname("pgtypes")]
        self.cpp_info.components["pgtypes"].requires = ["_common"]

        self.cpp_info.components["ecpg"].set_property("pkg_config_name", "libecpg")
        self.cpp_info.components["ecpg"].libs = [self._libname("ecpg")]
        self.cpp_info.components["ecpg"].requires = ["_common", "pgtypes", "pq"]

        self.cpp_info.components["ecpg_compat"].set_property("pkg_config_name", "libecpg_compat")
        self.cpp_info.components["ecpg_compat"].libs = [self._libname("ecpg_compat")]
        self.cpp_info.components["ecpg_compat"].requires = ["_common", "ecpg", "pgtypes"]

        mod_requires = []
        if self.options.with_nls:
            mod_requires.append("libgettext::libgettext")
        if self.options.get_safe("with_selinux"):
            mod_requires.append("libselinux::libselinux")
        if self.options.with_uuid:
            mod_requires.append("util-linux-libuuid::util-linux-libuuid")
        if self.options.with_libxml:
            mod_requires.append("libxml2::libxml2")
        if self.options.with_libxslt:
            mod_requires.append("libxslt::libxslt")
        self.cpp_info.components["_modules"].requires = mod_requires

        tool_requires = []
        if self.options.with_nls:
            tool_requires.append("libgettext::libgettext")
        if self.options.with_gssapi:
            tool_requires.append("krb5::krb5-gssapi")
        if self.options.get_safe("with_icu"):
            tool_requires.extend(["icu::icu-uc", "icu::icu-i18n"])
        if self.options.with_ldap:
            tool_requires.append("openldap::openldap")
        if self.options.get_safe("with_lz4"):
            tool_requires.append("lz4::lz4")
        if self.options.get_safe("with_pam"):
            tool_requires.append("linux-pam::pam")
        if self.options.get_safe("with_readline") == "readline":
            tool_requires.append("readline::readline")
        elif self.options.get_safe("with_readline") == "editline":
            tool_requires.append("editline::editline")
        if self.options.get_safe("with_systemd"):
            tool_requires.append("libsystemd::libsystemd")
        if self.options.with_libxml:
            tool_requires.append("libxml2::libxml2")
        if self.options.with_zlib:
            tool_requires.append("zlib::zlib")
        if self.options.with_zstd:
            tool_requires.append("zstd::zstd")
        self.cpp_info.components["_tools"].requires = tool_requires

        self.runenv_info.define_path("PostgreSQL_ROOT", self.package_folder)

        self.cpp_info.names["cmake_find_package"] = "PostgreSQL"
        self.cpp_info.names["cmake_find_package_multi"] = "PostgreSQL"
        self.env_info.PostgreSQL_ROOT = self.package_folder
