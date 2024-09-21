import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class I2cConan(ConanFile):
    name = "i2c-tools"
    description = "I2C tools for the linux kernel as well as an I2C library."
    license = ("GPL-2.0-or-later", "LGPL-2.1")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://i2c.wiki.kernel.org/index.php/I2C_Tools"
    topics = ("i2c",)

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

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("linux-headers-generic/5.15.128")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("i2c-tools only support Linux")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        shared = "1" if self.options.shared else "0"
        not_shared = "1" if not self.options.shared else "0"
        tc.make_args = [
            "PREFIX=/",
            f"BUILD_DYNAMIC_LIB={shared}",
            f"BUILD_STATIC_LIB={not_shared}",
            f"USE_STATIC_LIB={not_shared}",
        ]
        tc.generate()

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "Makefile"),
            "SRCDIRS	:= include lib eeprom stub tools $(EXTRA)",
            "SRCDIRS	:= include lib $(EXTRA)",
        )

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def package(self):
        copy(self, "COPYING",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYING.LGPL",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["i2c"]
