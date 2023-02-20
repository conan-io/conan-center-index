from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager

required_conan_version = ">=1.47"


class SysConfigEGLConan(ConanFile):
    name = "egl"
    version = "system"
    description = "cross-platform virtual conan package for the EGL support"
    topics = ("conan", "opengl", "egl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.khronos.org/egl"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipes supports only Linux and FreeBSD")

    def package_id(self):
        self.info.clear()

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["mesa-libEGL-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["mesa-libEGL-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install_substitutes(["libegl-dev", "libegl1-mesa-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["libglvnd"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["Mesa-libEGL-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["libglvnd"], update=True, check=True)

    def package_info(self):
        # TODO: Workaround for #2311 until a better solution can be found
        self.cpp_info.filenames["cmake_find_package"] = "egl_system"
        self.cpp_info.filenames["cmake_find_package_multi"] = "egl_system"

        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        pkg_config = PkgConfig(self, "egl")
        pkg_config.fill_cpp_info(self.cpp_info, is_system=True)

