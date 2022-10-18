from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.system import package_manager
from conans import tools

required_conan_version = ">=1.47"


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
        self.info.header_only()

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
        dnf = package_manager.Dnf(self)
        dnf.install(["libvdpau-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["libvdpau-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libvdpau-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["libvdpau"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["libvdpau-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["libvdpau"], update=True, check=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self._fill_cppinfo_from_pkgconfig('vdpau')
