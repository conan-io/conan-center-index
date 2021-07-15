from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class WinPcapConan(ConanFile):
    name = "winpcap"
    description = "For many years, WinPcap has been recognized as the industry-standard tool for link-layer network access in Windows environments, " \
                  "allowing applications to capture and transmit network packets bypassing the protocol stack, and including kernel-level packet filtering, " \
                  "a network statistics engine and support for remote packet capture."
    license = "BSD-3-Clause"
    topics = ("conan", "packet", "capture", "filtering", "network", "protocol")
    homepage = "https://www.winpcap.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "capture_type": ["bpf", "dag", "dlpi", "enet", "nit", "null", "libdlpi", "linux", "pf", "sita", "snit", "snoop", "win32"],
        "remote": [True, False],
        "bluetooth": [True, False],
        "usb_sniffing": [True, False],
        "usb_sniffing_device": "ANY",
        "turbocap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "capture_type": "null",
        "remote": True,
        "bluetooth": False,
        "usb_sniffing": True,
        "usb_sniffing_device": "/dev/usbmon",
        "turbocap": False,
    }

    exports_sources = "CMakeLists.txt", "cmake/*", "patches/*"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.turbocap = True
            self.options.capture_type = "win32"
        elif self.settings.os == "Linux":
            self.options.capture_type = "linux"
        if self.settings.os != "Linux":
            del self.options.bluetooth
            del self.options.usb_sniffing
            del self.options.usb_sniffing_device

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.capture_type == "dag":
            # FIXME: missing dag recipe
            raise ConanInvalidConfiguration("missing dag cci recipe")
        if self.options.get_safe("bluetooth"):
            # FIXME: missing bluez recipe
            raise ConanInvalidConfiguration("missing bluez cci recipe")
        if self.options.turbocap and self.settings.os != "Windows":
            # FIXME: missing turbocap recipe
            raise ConanInvalidConfiguration("missing turbocap cci recipe")

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("bison/3.7.1")
            self.build_requires("flex/2.6.4")

    def validate(self):
        if self.settings.os == "Windows":
            if not self.options.remote:
                raise ConanInvalidConfiguration("os=Windows requires winpcap:remote=True")
            if not self.options.turbocap:
                raise ConanInvalidConfiguration("os=Windows requires winpcap:turbocap=True")
        elif self.settings.os == "Linux":
            if not str(self.options.usb_sniffing_device):
                raise ConanInvalidConfiguration("winpcap:usb_sniffing_device is invalid")
        else:
            raise ConanInvalidConfiguration("This recipe has not been tested/validated on os={}".format(self.settings.os))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WINPCAP_CAPTURE_TYPE"] = self.options.capture_type
        self._cmake.definitions["WINPCAP_REMOTE"] = self.options.remote
        self._cmake.definitions["WINPCAP_TURBOCAP"] = self.options.turbocap
        self._cmake.definitions["WINPCAP_BLUETOOTH"] = self.options.get_safe("bluetooth", False)
        self._cmake.definitions["WINPCAP_USB"] = self.options.get_safe("usb_sniffing", False)
        self._cmake.definitions["WINPCAP_USB_DEVICE"] = self.options.get_safe("usb_sniffing_device", "")
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=os.path.join(self._source_subfolder, "wpcap", "libpcap"), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.settings.os == "Windows":
            libs = ["wpcap", "packet"]
        else:
            libs = ["pcap"]
        self.cpp_info.libs = libs
        if self.options.get_safe("remote"):
            self.cpp_info.defines.append("HAVE_REMOTE")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
