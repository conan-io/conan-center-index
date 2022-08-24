from conan import ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration


class ConanGTK(ConanFile):
    name = "gtk"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    homepage = "https://www.gtk.org"
    description = "A free and open-source cross-platform widget toolkit for creating graphical user interfaces"
    settings = "os"
    options = {"version": [2, 3]}
    default_options = {"version": 2}
    topics = ("gui", "widget", "graphical")

    def configure(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")
    
    def package_id(self):
        self.info.settings.clear()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("GTK-{} development files aren't available, give up.".format(self.options.version))
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
        packages = []
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if tools.os_info.with_apt:
                packages = ["libgtk2.0-dev"] if self.options.version == 2 else ["libgtk-3-dev"]
            elif tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["gtk{}-devel".format(self.options.version)]
            elif tools.os_info.with_pacman:
                packages = ["gtk{}".format(self.options.version)]
            elif tools.os_info.with_zypper:
                packages = ["gtk{}-devel".format(self.options.version)]
            else:
                self.output.warn("Do not know how to install 'GTK-{}' for {}."
                                 .format(self.options.version,
                                         tools.os_info.linux_distro))
        if tools.os_info.is_freebsd and self.settings.os == "FreeBSD":
            packages = ["gtk{}".format(self.options.version)]
        if packages:
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            for p in packages:
                package_tool.install(update=True, packages=p)

    def package_info(self):
        for name in ["gtk+-{}.0".format(self.options.version)]:
            self._fill_cppinfo_from_pkgconfig(name)
