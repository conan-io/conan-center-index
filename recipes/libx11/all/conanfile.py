import os
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

    def system_requirements(self):
        installer = tools.SystemPackageTool()
        if not installer.installed(self._required_system_package):
            raise ConanInvalidConfiguration(
                "X11 compatibility requires {0}. Install {0} with something like: sudo apt-get install {0}"
                .format(self._required_system_package))

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "This library is only compatible with Linux")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _get_package_info(self, lib_name):
        ret = os.system("pkg-config --cflags --libs {}".format(lib_name))
        flags = shlex.split(ret)
        include_dirs = []
        lib_dirs = []
        libs = []
        for flag in flags:
            if flag[:2] == '-L':
                lib_dirs.append(flag[2:])
            elif flag[:2] == '-I':
                include_dirs.append(flag[2:])
            elif flag[:2] == '-l':
                libs.append(flag[2:])
        return include_dirs, lib_dirs, libs

    def package_info(self):
        includedirs, libdirs, libs = self._get_package_info("x11")
        self.cpp_info.libs.extend(libs)
        self.cpp_info.includedirs.extend(includedirs)
        self.cpp_info.libdirs.extend(libdirs)

    def package_id(self):
        self.info.header_only()
