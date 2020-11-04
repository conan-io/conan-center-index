from conans import ConanFile, tools
from conans.errors import ConanException


class ConanGTK(ConanFile):
    name = "gtkmm"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    homepage = "https://www.gtk.org"
    description = "The C++ API for GTK."
    settings = {"os": "Linux"}
    options = {"version": [2]}
    default_options = {"version": 2}
    topics = ("gui", "widget", "graphical")

    def package_id(self):
        self.info.settings.clear()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("gtkmm-{} development files aren't available, give up.".format(self.options.version))
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

    def _version(self):
        return self.options.version, 4

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            major,minor = self._version()
            full_version = "{}{}".format(major, minor)
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            if tools.os_info.with_apt:
                packages = ["libgtkmm-{}.{}-dev".format(major, minor)]
            elif tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["gtkmm{}-devel".format(full_version)]
            elif tools.os_info.with_pacman:
                packages = ["gtkmm".format(full_version)]
            elif tools.os_info.with_zypper:
                packages = ["gtkmm{}-devel".format(full_version)]
            else:
                self.output.warn("Do not know how to install 'gtkmm-{}' for {}."
                                 .format(full_version,
                                         tools.os_info.linux_distro))
                packages = []
            for p in packages:
                package_tool.install(update=True, packages=p)

    def package_info(self):
        major,minor = self._version()
        for name in ["gtkmm-{}.{}".format(major,minor)]:
            self._fill_cppinfo_from_pkgconfig(name)
