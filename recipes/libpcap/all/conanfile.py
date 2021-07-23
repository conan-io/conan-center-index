from conans import AutoToolsBuildEnvironment, tools, ConanFile
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibPcapConan(ConanFile):
    name = "libpcap"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/the-tcpdump-group/libpcap"
    description = "libpcap is an API for capturing network traffic"
    license = "BSD-3-Clause"
    topics = ("networking", "pcap", "sniffing", "network-traffic")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_libusb": [True, False],
        "enable_universal": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_libusb": False,
        "enable_universal": True
    }
    _autotools = None

    # TODO: Add dbus-glib when available
    # TODO: Add libnl-genl when available
    # TODO: Add libbluetooth when available
    # TODO: Add libibverbs when available

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.enable_libusb:
            self.requires("libusb/1.0.24")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("libpcap is not supported on Windows.")
        if tools.Version(self.version) < "1.10.0" and self.settings.os == "Macos" and self.options.shared:
            raise ConanInvalidConfiguration("libpcap {} can not be built as shared on OSX.".format(self.version))

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("bison/3.7.1")
            self.build_requires("flex/2.6.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            configure_args = ["--enable-shared" if self.options.shared else "--disable-shared"]
            configure_args.append("--disable-universal" if not self.options.enable_universal else "")
            configure_args.append("--enable-usb" if self.options.enable_libusb else "--disable-usb")
            configure_args.extend([
                "--without-libnl",
                "--disable-bluetooth",
                "--disable-packet-ring",
                "--disable-dbus",
                "--disable-rdma"
            ])
            if tools.cross_building(self.settings):
                target_os = "linux" if self.settings.os == "Linux" else "null"
                configure_args.append("--with-pcap=%s" % target_os)
            elif "arm" in self.settings.arch and self.settings.os == "Linux":
                configure_args.append("--host=arm-linux")
            self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")

    def package_info(self):
        self.cpp_info.names["pkg_config"]= "libpcap"
        self.cpp_info.libs = ["pcap"]
