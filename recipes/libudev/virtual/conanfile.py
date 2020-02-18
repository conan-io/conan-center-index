from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class LibudevConan(ConanFile):
    name = "libudev"
    description = "[Virtual package] Installs libudev via a system package manager"
    topics = ("virtual-package", "libudev")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/systemd/"
    license = "LGPL-2.1-or-later"
    
    settings = "os", "arch"

    def source(self):
        pass

    def config_options(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This package only provides support for Linux")
        if not (tools.os_info.with_apt 
            or tools.os_info.with_yum
            or tools.os_info.with_zypper
            or tools.os_info.with_pacman):
            raise ConanInvalidConfiguration("Only apt, yum, zypper and pacman are currently supported")

    def system_requirements(self):
        packages = ""
        if tools.os_info.with_apt:
            packages = "libudev-dev"
        elif tools.os_info.with_yum:
            packages = "libudev-devel"
        elif tools.os_info.with_zypper:
            packages = "libudev-devel"
        elif tools.os_info.with_pacman:
            packages = "libsystemd systemd"

        tools.SystemPackageTool().install(packages=packages)

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.system_libs.append("udev")
