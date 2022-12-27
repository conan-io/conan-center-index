from conan import ConanFile
from conan.errors import ConanException
from conan.tools.system import package_manager
from conan.tools.gnu import PkgConfig

required_conan_version = ">=1.47"


class SysConfigGLUConan(ConanFile):
    name = "glu"
    version = "system"
    description = "cross-platform virtual conan package for the GLU support"
    topics = ("opengl", "glu")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cgit.freedesktop.org/mesa/glu/"
    license = "SGI-B-2.0"
    settings = "os", "arch", "compiler", "build_type"
    requires = "opengl/system"

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["mesa-libGLU-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["mesa-libGLU-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libglu1-mesa-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["glu"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["glu-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["libGLU"], update=True, check=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["Glu32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self._fill_cppinfo_from_pkgconfig("glu")

    def package_id(self):
        self.info.clear()
