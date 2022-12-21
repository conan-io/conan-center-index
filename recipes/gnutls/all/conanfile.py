from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps, Autotools
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.53.0"


class GnuTLSConan(ConanFile):
    name = "gnutls"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnutls.org"
    description = "GnuTLS is a secure communications library implementing the SSL, TLS and DTLS protocols"
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "enable_cxx": [True, False],
               "with_zlib": [True, False],
               "with_zstd": [True, False],
               "with_brotli": [True, False],}
    default_options = {"shared": False,
                       "fPIC": True,
                       "enable_cxx": True,
                       "with_zlib": True,
                       "with_zstd": True,
                       "with_brotli": True,}

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_cxx:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nettle/3.8.1")
        self.requires("gmp/6.2.1")
        self.requires("libiconv/1.17")
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.with_brotli:
            self.requires("brotli/1.0.9")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} cannot be deployed by Visual Studio.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def generate(self):
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        yes_no = lambda v: "yes" if v else "no"
        autotoolstc = AutotoolsToolchain(self)
        autotoolstc.configure_args.extend([
                          "--disable-tests",
                          "--disable-doc",
                          "--disable-manpages",
                          "--disable-full-test-suite",
                          "--disable-maintainer-mode",
                          "--disable-option-checking",
                          "--without-p11-kit",
                          "--without-idn",
                          "--with-included-libtasn1",
                          "--with-included-unistring",
                          "--with-libiconv-prefix={}".format(self.dependencies["libiconv"].package_folder),
                          "--enable-shared={}".format(yes_no(self.options.shared)),
                          "--enable-static={}".format(yes_no(not self.options.shared)),
                          "--with-cxx={}".format(yes_no(self.options.enable_cxx)),
                          "--with-zlib={}".format(yes_no(self.options.with_zlib)),
                          "--with-brotli={}".format(yes_no(self.options.with_brotli)),
                          "--with-zstd={}".format(yes_no(self.options.with_zstd)),
                          ])

        autotoolstc.generate()
        autodeps = AutotoolsDeps(self)
        autodeps.generate()
        pkgdeps = PkgConfigDeps(self)
        pkgdeps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["gnutls", "gnutlsxx"] if self.options.enable_cxx else ["gnutls"]
        self.cpp_info.set_property("cmake_file_name", "GnuTLS")
        self.cpp_info.set_property("cmake_target_name", "GnuTLS::GnuTLS")
        self.cpp_info.set_property("pkg_config_name", "gnutls")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "GnuTLS"
        self.cpp_info.names["cmake_find_package_multi"] = "GnuTLS"
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
