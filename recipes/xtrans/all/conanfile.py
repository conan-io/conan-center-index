from conan import ConanFile
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.47"


class XtransConan(ConanFile):
    name = "xtrans"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://www.x.org/wiki/"
    description = "X Network Transport layer shared code"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("x11", "xorg")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This recipe supports only Linux and FreeBSD")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.arch
        del self.info.settings.build_type

    def system_requirements(self):
        apt = package_manager.Apt(self)
        apt.install(["xtrans-dev"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["xorg-x11-xtrans-devel"], update=True, check=True)

        dnf = package_manager.Dnf(self)
        dnf.install(["xorg-x11-xtrans-devel"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["xtrans"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["xtrans"], update=True, check=True)

        package_manager.Pkg(self).install(["xtrans"], update=True, check=True)

    def package_info(self):
        pkg_config = PkgConfig(self, "xtrans")
        pkg_config.fill_cpp_info(
            self.cpp_info, is_system=self.settings.os != "FreeBSD")
        self.cpp_info.version = pkg_config.version
        self.cpp_info.set_property("pkg_config_name", "xtrans")
        self.cpp_info.set_property("component_version", pkg_config.version)
        self.cpp_info.set_property("pkg_config_custom_content",
                                                    "\n".join(f"{key}={value}" for key, value in pkg_config.variables.items() if key not in ["pcfiledir","prefix", "includedir"]))
