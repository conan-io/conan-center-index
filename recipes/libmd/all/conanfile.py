import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"

class LibMDConan(ConanFile):
    name = "libmd"
    description = "Message Digest functions from BSD systems"
    license = "BSD-2-Clause AND BSD-3-Clause AND ISC AND Beerware AND DocumentRef-COPYING:LicenseRef-libmd-Public-Domain"
    homepage = "https://gitlab.freedesktop.org/libbsd/libmd"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("message-digest", "hash", "bsd",
              "md2", "md4", "md5", "ripemd", "rmd160",
              "sha", "sha1", "sha2", "sha256", "sha512")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def configure(self):
        if self.options.shared:
           self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmd")
        self.cpp_info.libs = ["md"]
