
import os

from conan import ConanFile, tools
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.files import chdir
from conan.errors import ConanException

required_conan_version = ">=1.33.0"

class BlueZConan(ConanFile):
    name = "bluez"
    generators = "pkg_config"
    
    license = "GPLv2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bluez.org/"
    description = "Official Linux Bluetooth protocol stack"
    topics = ("bluetooth", "linux")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_usb": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_usb": False
    }

    def config_options(self):
        if self.settings.os == "Windows":
            ConanException("Unable to build BlueZ on Windows")

    def requirements(self):
        self.requires("dbus/1.12.20")
        self.requires("glib/2.73.0")
        if self.options.with_usb:
            self.requires("libusb/1.0.26")
        if tools.Version(self.version) < "5.0":
            self.requires("flex/2.6.4")
            self.requires("bison/3.7.6")
        if tools.Version(self.version) >= "5.0":
            self.requires("readline/8.1.2")


    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def layout(self):
        basic_layout(self)

    def generate(self):
        at_toolchain = AutotoolsToolchain(self)
        at_toolchain.configure_args = [
            "--disable-service"
        ]
        at_toolchain.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ["bluetooth"]
