from conans import AutoToolsBuildEnvironment, tools, ConanFile
from conans.errors import ConanInvalidConfiguration
import os


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
        "enable_dbus": [True, False],
        "enable_bluetooth": [True, False],
        "enable_usb": [True, False],
        "enable_packet_ring": [True, False],
        "disable_universal": [True, False]
    }
    default_options = {
        'shared': False,
        'enable_dbus': False,
        'enable_bluetooth': False,
        'enable_usb': False,
        'enable_packet_ring': False,
        'disable_universal': False
    }
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _is_amd64_to_i386(self):
        return self.settings.arch == "x86" and tools.detected_architecture() == "x86_64"

    def requirements(self):
        if self.options.enable_usb:
            self.requires("libusb/1.0.23")

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("bison/3.7.1")
            self.build_requires("flex/2.6.4")

    def system_requirements(self):
        if self.settings.os == "Linux":
            arch = ":i386" if self._is_amd64_to_i386() else ""
            package_list = []
            if self.options.enable_dbus:
                package_list.extend(["libdbus-glib-1-dev%s" % arch, "libdbus-1-dev"])
            if self.options.enable_bluetooth:
                package_list.append("libbluetooth-dev%s" % arch)
            if self.options.enable_packet_ring:
                package_list.append("libnl-genl-3-dev%s" % arch)
            if package_list:
                package_tool = tools.SystemPackageTool(conanfile=self)
                package_tool.install(packages=" ".join(package_list), update=True)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("For Windows use winpcap/4.1.2@bincrafters/stable")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            configure_args = ["--prefix=%s" % self.package_folder]
            configure_args.append("--enable-shared" if self.options.shared else "--disable-shared")
            configure_args.append("--disable-universal" if not self.options.disable_universal else "")
            configure_args.append("--enable-dbus" if self.options.enable_dbus else "--disable-dbus")
            configure_args.append("--enable-bluetooth" if self.options.enable_bluetooth else "--disable-bluetooth")
            configure_args.append("--enable-usb" if self.options.enable_usb else "--disable-usb")
            configure_args.append("--enable-packet-ring" if self.options.enable_packet_ring else "--disable-packet-ring")
            if not self.options.enable_packet_ring:
                configure_args.append("--without-libnl")
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
            os.remove(os.path.join(self.package_folder, "lib", "libpcap.a"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            if self.options.enable_dbus:
                self.cpp_info.system_libs.append("dbus-glib-1")
                self.cpp_info.libs.append("dbus-1")
            if self.options.enable_bluetooth:
                self.cpp_info.system_libs.append("bluetooth")
            if self.options.enable_packet_ring:
                self.cpp_info.system_libs.append("nl-genl-3")
                self.cpp_info.system_libs.append("nl-3")
