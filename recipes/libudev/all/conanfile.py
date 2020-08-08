from conans import ConanFile, tools
from conans.errors import ConanException
import os


class LibudevConan(ConanFile):
    name = "libudev"
    version = "system"
    description = "API for enumerating and introspecting local devices"
    topics = ("conan", "udev")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://systemd.io/"
    license = "LGPL-2.1+"
    settings = {"os": "Linux"}

    def system_requirements(self):
        if tools.os_info.is_linux and self.settings.os == "Linux":
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode="verify")
            if tools.os_info.with_yum or tools.os_info.with_dnf:
                packages = ["libudev-devel"]
            elif tools.os_info.with_apt:
                packages = ["libudev-dev"]
            elif tools.os_info.with_pacman:
                packages = ["libsystemd", "systemd"]
            elif tools.os_info.with_zypper:
                packages = ["libudev-devel"]
            else:
                self.output.warn("Do not know how to install 'libudev' for {}.".format(tools.os_info.linux_distro))
                packages = []
            for p in packages:
                package_tool.install(update=True, packages=p)

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("udev development files aren't available, give up")
        libs = [lib[2:] for lib in pkg_config.libs_only_l]
        lib_dirs = [lib[2:] for lib in pkg_config.libs_only_L]
        ldflags = [flag for flag in pkg_config.libs_only_other]
        include_dirs = [include[2:] for include in pkg_config.cflags_only_I]
        cflags = [flag for flag in pkg_config.cflags_only_other if not flag.startswith("-D")]
        defines = [flag[2:] for flag in pkg_config.cflags_only_other if flag.startswith("-D")]

        self.cpp_info.system_libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_dirs)
        self.cpp_info.sharedlinkflags.extend(ldflags)
        self.cpp_info.exelinkflags.extend(ldflags)
        self.cpp_info.defines.extend(defines)
        self.cpp_info.includedirs.extend(include_dirs)
        self.cpp_info.cflags.extend(cflags)
        self.cpp_info.cxxflags.extend(cflags)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.include_dirs = []
        self.cpp_info.libdirs = []
        self._fill_cppinfo_from_pkgconfig("libudev")
