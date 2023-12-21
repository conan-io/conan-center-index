from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager

required_conan_version = ">=1.51.3"


class SysConfigGLUConan(ConanFile):
    name = "glu"
    version = "system"
    description = "cross-platform virtual conan package for the GLU support"
    topics = ("opengl", "glu")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cgit.freedesktop.org/mesa/glu/"
    license = "SGI-B-2.0"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def requirements(self):
        # - glu headers include opengl headers
        # - on Apple OS, glu is part of OpenGL framework, already managed by opengl recipe
        self.requires("opengl/system", transitive_headers=True, transitive_libs=is_apple_os(self))

    def package_id(self):
        self.info.clear()

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
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["glu32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            pkg_config = PkgConfig(self, 'glu')
            pkg_config.fill_cpp_info(self.cpp_info, is_system=self.settings.os != "FreeBSD")
