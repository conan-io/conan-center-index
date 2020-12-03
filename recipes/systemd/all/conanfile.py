from conans import ConanFile, tools
from conans.errors import ConanException


class SystemdConan(ConanFile):
    name = "systemd"
    version = "system"
    description = "System and service manager"
    topics = ("systemd", "udev")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://systemd.io/"
    license = "LGPL-2.1-or-later"
    settings = {"os": "Linux"}

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            if tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["systemd", "systemd-libs", "libudev-devel"]
            elif tools.os_info.with_apt:
                packages = ["libsystemd-dev", "libudev-dev", "systemd"]
            elif tools.os_info.with_pacman:
                packages = ["systemd", "systemd-libs"]
            elif tools.os_info.with_zypper:
                packages = ["systemd-devel", "libudev-devel", "systemd"]
            else:
                self.output.warn("Do not know how to install 'systemd' for {}.".format(tools.os_info.linux_distro))
                packages = []
            for p in packages:
                package_tool.install(update=True, packages=p)

    def _fill_cppinfo_from_pkgconfig(self, name, component_name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("{} development files aren't available, give up".format(name))
        libs = [lib[2:] for lib in pkg_config.libs_only_l]
        lib_dirs = [lib[2:] for lib in pkg_config.libs_only_L]
        ldflags = [flag for flag in pkg_config.libs_only_other]
        include_dirs = [include[2:] for include in pkg_config.cflags_only_I]
        cflags = [flag for flag in pkg_config.cflags_only_other if not flag.startswith("-D")]
        defines = [flag[2:] for flag in pkg_config.cflags_only_other if flag.startswith("-D")]

        self.cpp_info.components[component_name].system_libs = libs
        self.cpp_info.components[component_name].libdirs = lib_dirs
        self.cpp_info.components[component_name].sharedlinkflags = ldflags
        self.cpp_info.components[component_name].exelinkflags = ldflags
        self.cpp_info.components[component_name].defines = defines
        self.cpp_info.components[component_name].includedirs = include_dirs
        self.cpp_info.components[component_name].cflags = cflags
        self.cpp_info.components[component_name].cxxflags = cflags

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self._fill_cppinfo_from_pkgconfig("systemd", "libsystemd")
        self._fill_cppinfo_from_pkgconfig("libudev", "udev")
