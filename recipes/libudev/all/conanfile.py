from conan import ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration


class LibUDEVConan(ConanFile):
    name = "libudev"
    version = "system"
    description = "API for enumerating and introspecting local devices"
    topics = ("udev", "devices", "enumerating")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/software/systemd/man/udev.html"
    license = "GPL-2.0-or-later", "LGPL-2.1-or-later"
    settings = "os"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libudev is only supported on Linux.")

    def package_id(self):
        self.info.header_only()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("libudev development files aren't available, give up")
        libs = [lib[2:] for lib in pkg_config.libs_only_l]
        lib_dirs = [lib[2:] for lib in pkg_config.libs_only_L]
        ldflags = [flag for flag in pkg_config.libs_only_other]
        include_dirs = [include[2:] for include in pkg_config.cflags_only_I]
        cflags = [flag for flag in pkg_config.cflags_only_other if not flag.startswith("-D")]
        defines = [flag[2:] for flag in pkg_config.cflags_only_other if flag.startswith("-D")]

        self.cpp_info.system_libs = libs
        self.cpp_info.libdirs = lib_dirs
        self.cpp_info.sharedlinkflags = ldflags
        self.cpp_info.exelinkflags = ldflags
        self.cpp_info.defines = defines
        self.cpp_info.includedirs = include_dirs
        self.cpp_info.cflags = cflags
        self.cpp_info.cxxflags = cflags

    def system_requirements(self):
        packages = []
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if tools.os_info.with_yum:
                packages = ["systemd-devel"]
            elif tools.os_info.with_apt:
                packages = ["libudev-dev"]
            elif tools.os_info.with_pacman:
                packages = ["systemd-libs"]
            elif tools.os_info.with_zypper:
                packages = ["libudev-devel"]
            else:
                self.output.warn("Don't know how to install %s for your distro." % self.name)
        if packages:
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')
            for p in packages:
                package_tool.install(update=True, packages=p)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self._fill_cppinfo_from_pkgconfig("libudev")
