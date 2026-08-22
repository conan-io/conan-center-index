import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import chdir, copy, get, rm, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class OpenldapConan(ConanFile):
    name = "openldap"
    description = "OpenLDAP C library"
    license = "OLDAP-2.8"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openldap.org/"
    topics = ("ldap", "load-balancer", "directory-access")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cyrus_sasl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cyrus_sasl": True,
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        if self.options.with_cyrus_sasl:
            self.requires("cyrus-sasl/2.1.28")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration(f"{self.name} is only supported on Unix platforms")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        def yes_no(v):
            return "yes" if v else "no"

        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            "--with-cyrus_sasl={}".format(yes_no(self.options.with_cyrus_sasl)),
            "--without-fetch",
            "--with-tls=openssl",
            "--enable-auditlog",
            "--libexecdir=${prefix}/bin",
            f"systemdsystemunitdir={os.path.join(self.package_folder, 'res')}",
        ]
        if cross_building(self):
            # When cross-building, yielding_select should be explicit:
            # https://git.openldap.org/openldap/openldap/-/blob/OPENLDAP_REL_ENG_2_5/configure.ac#L1636
            tc.configure_args.append("--with-yielding_select=yes")
            # Workaround: https://bugs.openldap.org/show_bug.cgi?id=9228
            tc.configure_args.append("ac_cv_func_memcmp_working=yes")
        if is_apple_os(self):
            # macOS Ventura does not have soelim, but mandoc_soelim
            tc.make_args.append("SOELIM=soelim" if shutil.which("soelim") else "SOELIM=mandoc_soelim")
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "configure"),
                        "WITH_SYSTEMD=no\nsystemdsystemunitdir=", "WITH_SYSTEMD=no")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rm(self, "*.la", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)
        for folder in ["var", "share", "etc", os.path.join("lib", "pkgconfig"), "home", "Users"]:
            rmdir(self, os.path.join(self.package_folder, folder))

    def package_info(self):
        self.cpp_info.components["ldap"].set_property("pkg_config_name", "ldap")
        self.cpp_info.components["ldap"].libs = ["ldap"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ldap"].system_libs = ["pthread", "resolv"]
        self.cpp_info.components["ldap"].requires = ["lber", "openssl::ssl", "openssl::crypto"]
        if self.options.with_cyrus_sasl:
            self.cpp_info.components["ldap"].requires.append("cyrus-sasl::cyrus-sasl")

        self.cpp_info.components["lber"].set_property("pkg_config_name", "lber")
        self.cpp_info.components["lber"].libs = ["lber"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["lber"].system_libs = ["pthread"]

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
