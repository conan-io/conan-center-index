import os
import subprocess
import shlex

from conans import ConanFile, CMake, tools


class LibX11Conan(ConanFile):
    name = "libx11"
    license = "X11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.x.org/wiki/"
    description = "Client interface to the X Window System, otherwise known as \'Xlib\'",
    settings = "os", "compiler", "build_type", "arch"
    _required_system_package = "libx11-dev"
    _system_package_tool = None

    def _system_packages(self):
        if not self._system_package_tool:
            self._system_package_tool = tools.SystemPackageTool()
        return self._system_package_tool

    def system_requirements(self):
        installer = self._system_packages()
        if not installer.installed(self._required_system_package):
            raise ConanInvalidConfiguration(
                "{0} system library missing. Install {0} in your system with something like: "\
                "sudo apt-get install {0}-dev"
                .format(self._required_system_package))

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "This library is only compatible with Linux")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _populate_cpp_info(self, lib_name):
        def get_value(arg, prefix):
            return arg[len(prefix):] if arg[:len(prefix)] == prefix else ""

        ret = subprocess.check_output("pkg-config --cflags --libs {}".format(lib_name), shell=True)
        args = shlex.split(ret)
        self.cpp_info.includedirs.extend([get_value(arg, '-L') for arg in args if get_value(arg, '-L') != ""])
        self.cpp_info.libdirs.extend([get_value(arg, '-I') for arg in args if get_value(arg, '-I') != ""])
        self.cpp_info.libs.extend([get_value(arg, '-l') for arg in args if get_value(arg, '-l') != ""])
        self.cpp_info.defines.extend([get_value(arg, '-D') for arg in args if get_value(arg, '-D') != ""])

    def package_info(self):
        if self._system_packages().installed("pkg-config"):
            self._populate_cpp_info("x11")
        else:
            self.cpp_info.libs.append("X11")

    def package_id(self):
        self.info.header_only()
