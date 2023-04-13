from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager

required_conan_version = ">=1.47"


class SysConfigVDPAUConan(ConanFile):
    name = "vdpau"
    version = "system"
    description = "VDPAU is the Video Decode and Presentation API for UNIX. It provides an interface to video decode acceleration and presentation hardware present in modern GPUs."
    topics = ("hwaccel", "video")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/VDPAU/"
    license = "MIT"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.arch
        del self.info.settings.build_type

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
            pkg_config = PkgConfig(self, "vdpau")
            pkg_config.fill_cpp_info(self.cpp_info)
