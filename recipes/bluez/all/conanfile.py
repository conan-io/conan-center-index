from conan import ConanFile
from conans import tools
from conan.tools.gnu import AutotoolsToolchain, PkgConfigDeps, AutotoolsDeps, Autotools
from conan.tools.layout import basic_layout
from conan.errors import ConanException

required_conan_version = ">=1.33.0"

class BlueZConan(ConanFile):
    name = "bluez"

    license = "GPL-2.0-or-later"
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
        "with_usb": [True, False],
        "with_udev": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_usb": False,
        "with_udev": False
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if not self.settings.os == "Linux":
            ConanException(f"Unable to build BlueZ on {self.settings.os}")
 
     def configure(self):
         if self.options.shared:
             del self.options.fPIC
         del self.settings.compiler.libcxx
         del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("dbus/1.12.20")
        self.requires("glib/2.73.0")
        if self.options.with_udev:
            self.requires("libudev/system")
        if tools.Version(self.version) >= "5.0":
            self.requires("readline/8.1.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def layout(self):
        basic_layout(self)

    def generate(self):
        at_toolchain = AutotoolsToolchain(self)
        at_toolchain.configure_args = [
            "--disable-tools",
            "--disable-client",
            "--disable-systemd",
            "--disable-monitor",
            "--disable-service",
            "--disable-manpages",
            "--disable-datafiles"
        ]
        if self.options.with_usb:
            at_toolchain.configure_args.append("--enable-usb")
        at_toolchain.generate()
        pc_deps = PkgConfigDeps(self)
        pc_deps.generate()

    def _config_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = Autotools(self, build_script_folder=self._source_subfolder)
        self._autotools.configure()
        return self._autotools

    def build(self):
        autotools = self._config_autotools()
        autotools.make()

    def package(self):
        autotools = self._config_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "bluetooth")
        self.cpp_info.set_property("cmake_file_name", "bluez")
        self.cpp_info.set_property("cmake_target_name", "bluez::bluez")
        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "bluez"
        self.cpp_info.names["cmake_find_package_multi"] = "bluez"
        self.cpp_info.names["pkg_config"] = "bluetooth"
        self.cpp_info.libs = ["bluetooth"]
