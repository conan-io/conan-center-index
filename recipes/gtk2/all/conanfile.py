from conans import ConanFile, tools
from conans.errors import ConanException


class ConanGTK2(ConanFile):
    name = "gtk2"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    homepage = "https://www.gtk.org"
    description = "A free and open-source cross-platform widget toolkit for creating graphical user interfaces"
    settings = {"os": "Linux"}
    topics = ("gui", "widget", "graphical")

    def package_id(self):
        self.info.header_only()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("GTK-2 development files aren't available, give up.")
        libs = [lib[2:] for lib in pkg_config.libs_only_l]
        lib_dirs = [lib[2:] for lib in pkg_config.libs_only_L]
        ldflags = [flag for flag in pkg_config.libs_only_other]
        include_dirs = [include[2:] for include in pkg_config.cflags_only_I]
        cflags = [flag for flag in pkg_config.cflags_only_other if not flag.startswith("-D")]
        defines = [flag[2:] for flag in pkg_config.cflags_only_other if flag.startswith("-D")]

        self.cpp_info.components[name].system_libs = libs
        self.cpp_info.components[name].libdirs = lib_dirs
        self.cpp_info.components[name].sharedlinkflags = ldflags
        self.cpp_info.components[name].exelinkflags = ldflags
        self.cpp_info.components[name].defines = defines
        self.cpp_info.components[name].includedirs = include_dirs
        self.cpp_info.components[name].cflags = cflags
        self.cpp_info.components[name].cxxflags = cflags

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            if tools.os_info.with_apt:
                packages = ["libgtk2.0-dev"]
            elif tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["gtk2-devel"]
            elif tools.os_info.with_pacman:
                packages = ["gtk2"]
            elif tools.os_info.with_zypper:
                packages = ["gtk2-devel"]
            else:
                self.output.warn("Do not know how to install 'GTK-2' for {}.".format(tools.os_info.linux_distro))
                packages = []
            for p in packages:
                package_tool.install(update=True, packages=p)

    def package_info(self):
        for name in ["gtk+-2.0"]:
            self._fill_cppinfo_from_pkgconfig(name)
