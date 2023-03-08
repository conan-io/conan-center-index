from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager

required_conan_version = ">=1.47"


class SysConfigVAAPIConan(ConanFile):
    name = "vaapi"
    version = "system"
    description = "VA-API is an open-source library and API specification, which provides access to graphics hardware acceleration capabilities for video processing."
    topics = ("conan", "vaapi", "hwaccel", "video")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://01.org/linuxmedia/vaapi"
    license = "MIT"
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
        dnf.install(["libva-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["libva-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libva-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["libva"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["libva-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["libva"], update=True, check=True)

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            for name in ['libva', 'libva-x11', 'libva-drm']:
                pkg_config = PkgConfig(self, name)
                self.cpp_info.components[name].includedirs = []
                self.cpp_info.components[name].libdirs = []
                pkg_config.fill_cpp_info(self.cpp_info.components[name])
