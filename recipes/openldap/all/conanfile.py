import os
from conan import ConanFile
from conan.tools.files import get, apply_conandata_patches, rmdir, rm, copy
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
required_conan_version = ">=1.55"


class OpenldapConan(ConanFile):
    name = "openldap"
    description = "OpenLDAP C++ library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openldap.org/"
    license = "OLDAP-2.8"
    topics = ("ldap", "load-balancer", "directory-access")
    exports_sources = ["patches/*"]
    settings = settings = "os", "compiler", "build_type", "arch"
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
    short_paths = True

    def layout(self):
        basic_layout(self, src_folder="src")
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("openssl/1.1.1t")
        if self.options.with_cyrus_sasl:
            self.requires("cyrus-sasl/2.1.27")

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                f"{self.ref} is only supported on Linux")

    def generate(self):
        def yes_no(v): return "yes" if v else "no"
        autotools_tc = AutotoolsToolchain(self)
        autotools_tc.update_configure_args({
            "--with-cyrus_sasl": yes_no(self.options.with_cyrus_sasl),
            "--with-pic": yes_no(self.options.get_safe("fPIC", True)),
            "--without-fetch": "",
            "--with-tls": "openssl",
            "--enable-auditlog": "",
            "--libexecdir": "${prefix}/bin"
        })
        
        env = autotools_tc.environment()
        env.define("systemdsystemunitdir", os.path.join(self.package_folder, "res"))
        autotools_tc.generate(env)

        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        for folder in ["var", "share", "etc", "lib/pkgconfig", "res", "root", "libexec", "home"]:
            rmdir(self, os.path.join(self.package_folder, folder))
        rm(self, pattern="*.la", folder=os.path.join( self.package_folder,"lib"), recursive=True)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
        self.output.info(
            "Appending PATH environment variable: {}".format(bin_path))

        self.cpp_info.libs = ["ldap", "lber"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
