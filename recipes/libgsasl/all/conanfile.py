from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class LibgsaslConan(ConanFile):
    name = "libgsasl"
    description = "Portable gsasl C library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gsasl/"
    license = "BSD-3-Clause"
    topics = ("libgsasl")

    description = "GNU Simple Authentication and Security Layer"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "ntlm": [False, True]
    }
    default_options = {"shared": False, "ntlm" : False}
    requires = ("libiconv/1.17",
                "libidn/1.36"
                )

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        yes_no = lambda v: "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-ntlm=%s"  % yes_no(self.options.ntlm))
        tc.generate()

    def build(self):
        # apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "gsasl")
        self.cpp_info.libs = ["gsasl"]
