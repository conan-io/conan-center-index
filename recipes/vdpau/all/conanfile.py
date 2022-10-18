from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conans import tools


class SysConfigVDPAUConan(ConanFile):
    name = "vdpau"
    version = "system"
    description = "VDPAU is the Video Decode and Presentation API for UNIX. It provides an interface to video decode acceleration and presentation hardware present in modern GPUs."
    topics = ("conan", "vdpau", "hwaccel", "video")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/VDPAU/"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")
    
    def package_id(self):
        self.info.settings.clear()

    def _fill_cppinfo_from_pkgconfig(self, name):
        pkg_config = tools.PkgConfig(name)
        if not pkg_config.provides:
            raise ConanException("VDPAU development files aren't available, give up")
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

    def system_requirements(self):
        packages = []
        if tools.os_info.is_linux and self.settings.os == "Linux":
            if tools.os_info.with_yum:
                packages = ["libvdpau-devel"]
            elif tools.os_info.with_apt:
                packages = ["libvdpau-dev"]
            elif tools.os_info.with_pacman:
                packages = ["libvdpau"]
            elif tools.os_info.with_zypper:
                packages = ["libvdpau-devel"]
            else:
                self.output.warn("Don't know how to install %s for your distro." % self.name)
        elif tools.os_info.is_freebsd and self.settings.os == "FreeBSD":
            packages = ["libvdpau"]
        if packages:
            package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')
            for p in packages:
                package_tool.install(update=True, packages=p)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self._fill_cppinfo_from_pkgconfig('vdpau')
