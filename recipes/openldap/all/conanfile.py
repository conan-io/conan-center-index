import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rm, rmdir, move_folder_contents
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class OpenldapConan(ConanFile):
    name = "openldap"
    description = "OpenLDAP C++ library"
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

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        if self.options.with_cyrus_sasl:
            self.requires("cyrus-sasl/2.1.28")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"{self.name} is only supported on Linux")
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

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
            f"systemdsystemunitdir={os.path.join(self.package_folder, 'res')}",
        ]
        # Need to link to -pthread instead of -lpthread for gcc 8 shared=True
        # on CI job. Otherwise, linking fails.
        # tc.libs.remove("pthread")
        # self._configure_vars["LIBS"] = self._configure_vars["LIBS"].replace("-lpthread", "-pthread")
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
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
        if os.path.exists(os.path.join(self.source_folder, "libexec")):
            move_folder_contents(self, os.path.join(self.source_folder, "libexec"),
                                 os.path.join(self.package_folder, "bin"))
        rm(self, "*.la", self.package_folder, recursive=True)
        # Remove symlinks to libexec/slapd
        for path in self.package_path.joinpath("bin").glob("slap*"):
            if path.is_symlink():
                path.unlink()
        # Remove irrelevant directories
        for folder in ["var", "share", "etc", os.path.join("lib", "pkgconfig"), "res", "home", "libexec"]:
            if os.path.exists(os.path.join(self.package_folder, folder)):
                rmdir(self, os.path.join(self.package_folder, folder))

    def package_info(self):
        self.cpp_info.libs = ["ldap", "lber"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

        # TODO: to remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
