import os
import subprocess
import shlex

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s


class LibX11Conan(ConanFile):
    name = "libx11"
    license = "X11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.x.org/wiki/"
    description = "Client interface to the X Window System, otherwise known as \'Xlib\'",
    settings = "os", "compiler", "build_type", "arch"
    _required_system_package = "libx11-dev"

    def system_requirements(self):
        installer = tools.SystemPackageTool()
        if not installer.installed(self._required_system_package):
            raise ConanInvalidConfiguration(
                "{0} system library missing. Install {0} in your system with something like: "\
                "sudo apt-get install {0}"
                .format(self._required_system_package))

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "This library is only compatible with Linux")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package(self):
        tools.download("https://gitlab.freedesktop.org/xorg/lib/libx11/raw/master/COPYING", filename="COPYING")
        self.copy("COPYING", dst="licenses")


    def package_info(self):
        if tools.which("pkg-config"):
            pkg = tools.PkgConfig("x11")
            self.cpp_info.includedirs = [remove_prefix(x,'-I') for x in pkg.cflags_only_I]
            self.cpp_info.libdirs = [remove_prefix(x,'-L') for x in pkg.libs_only_L]
            self.cpp_info.libs = [remove_prefix(x,'-l') for x in pkg.libs_only_l]
            self.cpp_info.defines = [remove_prefix(x,'-D') for x in pkg.cflags_only_other if x.startswith('-D')]
            self.cpp_info.cflags = [x for x in pkg.cflags_only_other if not x.startswith('-D')]
            self.cpp_info.cppflags = [x for x in pkg.cflags_only_other if not x.startswith('-D')]
            self.cpp_info.sharedlinkflags = pkg.libs_only_other
            self.cpp_info.exelinkflags = pkg.libs_only_other
        else:
            self.cpp_info.libs.append("X11")

    def package_id(self):
        self.info.header_only()
