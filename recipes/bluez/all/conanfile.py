from conan import ConanFile
from conans import tools
from conan.tools.gnu import AutotoolsToolchain, AutotoolsDeps, Autotools
from conan.tools.layout import basic_layout
from conan.errors import ConanException

required_conan_version = ">=1.33.0"

class BlueZConan(ConanFile):
    name = "bluez"

    license = "GPLv2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bluez.org/"
    description = "Official Linux Bluetooth protocol stack"
    topics = ("bluetooth", "linux")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "patches/*"
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

    _autotools = None

    @property
    def _source_subfolder(self):
        return "."

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
        tc = AutotoolsToolchain(self)
        tc.configure_args = [
            "--disable-service"
        ]
        if self.options.with_usb:
            tc.configure_args.append("--enable-usb")
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def _config_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = Autotools(self)
        self._autotools.autoreconf()
        self._autotools.configure()
        return self._autotools

    def build(self):
        autotools = self._config_autotools()
        autotools.make()

    def package(self):
        autotools = self._config_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "bluez"
        self.cpp_info.names["cmake_find_package_multi"] = "bluez"
        self.cpp_info.names["pkg_config"] = "bluetooth"
        self.cpp_info.libs = ["bluetooth"]
