from conan import ConanFile
from conan.tools.system import package_manager
from conan.tools.gnu import PkgConfig

required_conan_version = ">=1.50.0"


class SysConfigOpenGLConan(ConanFile):
    name = "opengl"
    version = "system"
    description = "cross-platform virtual conan package for the OpenGL support"
    topics = ("opengl", "gl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.opengl.org/"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install_substitutes(["libglvnd-devel"], ["mesa-libGL-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["mesa-libGL-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install_substitutes(["libgl-dev"], ["libgl1-mesa-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["libglvnd"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["Mesa-libGL-devel", "glproto-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["libglvnd"], update=True, check=True)

    def package_info(self):
        # TODO: Workaround for #2311 until a better solution can be found
        self.cpp_info.filenames["cmake_find_package"] = "opengl_system"
        self.cpp_info.filenames["cmake_find_package_multi"] = "opengl_system"

        self.cpp_info.set_property("cmake_file_name", "opengl_system")

        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        if self.settings.os == "Macos":
            self.cpp_info.defines.append("GL_SILENCE_DEPRECATION=1")
            self.cpp_info.frameworks.append("OpenGL")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["opengl32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            pkg_config = PkgConfig(self, 'gl')
            pkg_config.fill_cpp_info(self.cpp_info, is_system=self.settings.os != "FreeBSD")
