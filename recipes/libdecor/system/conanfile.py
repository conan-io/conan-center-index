from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager

required_conan_version = ">=1.50.0"


class SysConfigLibdecorConan(ConanFile):
    name = "libdecor"
    version = "system"
    description = "virtual conan package for the libdecor client-side Wayland decoration library"
    topics = ("wayland", "libdecor", "decoration")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.freedesktop.org/libdecor/libdecor"
    license = "MIT"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["libdecor-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["libdecor-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libdecor-0-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["libdecor"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["libdecor-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["libdecor"], update=True, check=True)

        alpine = package_manager.Apk(self)
        alpine.install(["libdecor-dev"], update=True, check=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("pkg_config_name", "libdecor-0")
        pkg_config = PkgConfig(self, "libdecor-0")
        pkg_config.fill_cpp_info(self.cpp_info, is_system=True)
