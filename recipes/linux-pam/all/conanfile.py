import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, mkdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain

required_conan_version = ">=1.53.0"

class LinuxPamConan(ConanFile):
    name = "linux-pam"
    description = "Pluggable Authentication Modules for Linux"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/linux-pam/linux-pam"
    topics = ("pam", "pluggable-authentication-module", "authentication", "security")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_db": ["db", "gdbm", False],
        "with_intl": [True, False],
        "with_nis": [True, False],
        "with_openssl": [True, False],
        "with_selinux": [True, False],
        "with_systemd": [True, False],
        # TODO:
        # "with_audit": [True, False],
        # "with_econf": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_db": "gdbm",
        "with_intl": True,  # cannot currently be disabled due to a build.meson bug
        "with_nis": False,
        "with_openssl": True,
        "with_selinux": True,
        "with_systemd": True,
    }
    options_description = {
        "with_db": "Build pam_userdb module with specified database backend",
        "with_intl": "Enable i18n support using libintl from libgettext",
        "with_nis": "Enable NIS/YP support in pam_unix using libnsl",
        "with_openssl": "Use OpenSSL crypto libraries in pam_timestamp",
        "with_selinux": "Enable SELinux support",
        "with_systemd": "Enable logind support in pam_issue and pam_timestamp",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_db == "db":
            self.requires("libdb/5.3.28")
        elif self.options.with_db == "gdbm":
            self.requires("gdbm/1.23")
        if self.options.with_intl:
            self.requires("libgettext/0.22")
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_selinux:
            self.requires("libselinux/3.6")
        if self.options.with_systemd:
            self.requires("libsystemd/255.10")

    def validate(self):
        if is_apple_os(self) or self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.settings.os} is not supported.")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        feature = lambda option: "enabled" if option else "disabled"

        tc = MesonToolchain(self)
        tc.project_options["docs"] = "disabled"
        tc.project_options["examples"] = "false"
        tc.project_options["xtests"] = "false"
        tc.project_options["audit"] = feature(self.options.get_safe("with_audit"))
        tc.project_options["econf"] = feature(self.options.get_safe("with_econf"))
        tc.project_options["i18n"] = feature(self.options.with_intl)
        tc.project_options["logind"] = feature(self.options.with_systemd)
        tc.project_options["nis"] = feature(self.options.with_nis)
        tc.project_options["openssl"] = feature(self.options.with_openssl)
        tc.project_options["selinux"] = feature(self.options.with_selinux)
        tc.project_options["pam_userdb"] = feature(self.options.with_db)
        tc.project_options["db"] = str(self.options.with_db) if self.options.with_db else "auto"
        # Override auto value
        tc.project_options["pam_unix"] = "enabled"

        # To help find_library() calls in Meson
        if self.options.with_db:
            db_pkg = "libdb" if self.options.with_db == "db" else "gdbm"
            db = self.dependencies[db_pkg].cpp_info.aggregated_components()
            tc.extra_cflags.append('-I' + db.includedir)
            tc.extra_ldflags.append('-L' + db.libdir)

        tc.generate()

        deps = PkgConfigDeps(self)
        deps.set_property("libgettext", "pkg_config_name", "intl")
        deps.generate()

        VirtualBuildEnv(self).generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)
        # Move non-library files under res/
        mkdir(self, os.path.join(self.package_folder, "res"))
        for path in ["etc", "share", "var", os.path.join("lib", "systemd")]:
            if os.path.exists(os.path.join(self.package_folder, path)):
                shutil.move(os.path.join(self.package_folder, path),
                            os.path.join(self.package_folder, "res", path))

    def package_info(self):
        self.cpp_info.components["pam"].set_property("pkg_config_name", "pam")
        self.cpp_info.components["pam"].libs = ["pam"]
        self.cpp_info.components["pam"].libdirs.append(os.path.join("lib", "security"))
        self.cpp_info.components["pam"].resdirs = ["res"]
        if self.options.with_intl:
            self.cpp_info.components["pam"].requires.append("libgettext::libgettext")

        self.cpp_info.components["pamc"].set_property("pkg_config_name", "pamc")
        self.cpp_info.components["pamc"].libs = ["pamc"]

        self.cpp_info.components["pam_misc"].set_property("pkg_config_name", "pam_misc")
        self.cpp_info.components["pam_misc"].libs = ["pam_misc"]
        self.cpp_info.components["pam_misc"].requires = ["pam"]

        # Most of the dependencies are used by the modules in lib/security/
        requires = ["pam"]
        if self.options.with_db == "db":
            requires.append("libdb::libdb")
        elif self.options.with_db == "gdbm":
            requires.append("gdbm::gdbm")
        if self.options.with_openssl:
            requires.append("openssl::openssl")
        if self.options.with_selinux:
            requires.append("libselinux::libselinux")
        if self.options.with_systemd:
            requires.append("libsystemd::libsystemd")
        self.cpp_info.components["_modules"].requires = requires
        # if self.options.with_nis:
        #     self.cpp_info.components["_modules"].system_libs.append("nsl")
