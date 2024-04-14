import os
from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import rmdir, get, copy, rm, apply_conandata_patches, export_conandata_patches
from conan.tools.build import cross_building
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
required_conan_version = ">=1.43.0"


class OpenldapConan(ConanFile):
    name = "openldap"
    description = "OpenLDAP C++ library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openldap.org/"
    license = "OLDAP-2.8"
    topics = ("ldap", "load-balancer", "directory-access")
    exports_sources = ["patches/*"]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cyrus_sasl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cyrus_sasl": True
    }

    def layout(self):
        # src_folder must use the same source folder name the project
        basic_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("openssl/3.2.1")
        if self.options.with_cyrus_sasl:
            self.requires("cyrus-sasl/2.1.28")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                f"{self.name} is only supported on Linux")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        def yes_no(v): return "yes" if v else "no"
        tc.configure_args.extend([
            f"--with-cyrus_sasl={yes_no(self.options.with_cyrus_sasl)}",
            f"--with-pic={yes_no(self.options.get_safe('fPIC', True))}",
            "--without-fetch",
            "--with-tls=openssl",
            "--enable-auditlog"
        ])
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYRIGHT", self.source_folder, os.path.join(self.package_folder, "licenses"))
        for folder in ["var", "share", "etc", "lib/pkgconfig", "res", "libexec"]:
            rmdir(self, os.path.join(self.package_folder, folder))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*slap*", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
        self.output.info(
            f"Appending PATH environment variable: {bin_path}")

        self.cpp_info.libs = ["ldap", "lber"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
