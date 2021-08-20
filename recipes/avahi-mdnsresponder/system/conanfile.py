from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class AvahiMdnsResponderSystemConan(ConanFile):
    name = "avahi-mdnsresponder"
    provides = "mdnsresponder"
    version = "system"
    description = "Avahi - Service Discovery for Linux using mDNS/DNS-SD - compatible with Bonjour"
    topics = ("Avahi", "Bonjour", "DNS-SD", "mDNS")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lathiat/avahi"
    license = "LGPL-2.1-only"
    settings = "os"

    def validate(self):
        if self.settings.os != "Linux" or tools.cross_building(self):
            raise ConanInvalidConfiguration("Only Linux is supported for this package.")

    def system_requirements(self):
        packages = []
        if self.settings.os == "Linux" and tools.os_info.is_linux:
            # for building against Avahi Apple Bonjour compatibility library, libdns_sd and dns_sd.h are required
            if tools.os_info.with_apt:
                # Debian/Ubuntu
                packages = ["libavahi-compat-libdnssd-dev"]
            elif tools.os_info.with_yum:
                # RHEL/CentOS/Fedora
                packages = ["avahi-compat-libdns_sd-devel"]
            elif tools.os_info.with_pacman:
                # Arch Linux
                packages = ["avahi"]
            elif tools.os_info.with_zypper:
                # openSUSE
                packages = ["avahi-compat-mDNSResponder-devel"]
            else:
                self.output.warn("Do not know how to install Avahi Apple Bonjour compatibility library for {}.".format(tools.os_info.linux_distro))
        if packages:
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')
            for package in packages:
                package_tool.install(update=True, packages=package)

    def package_info(self):
        self.cpp_info.system_libs = ["dns_sd"]
