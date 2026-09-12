from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import PkgConfig
from conan.tools.system import package_manager

required_conan_version = ">=1.50.0"


class Webkit2gtkConan(ConanFile):
    name = "webkit2gtk"
    version = "system"
    description = "Web content engine library for GTK"
    topics = ("webkit", "gtk", "browser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://webkitgtk.org"
    license = "LGPL-2.1-or-later"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This recipe supports only Linux")

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["webkit2gtk4.1-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["webkit2gtk4.1-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libwebkit2gtk-4.1-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["webkit2gtk-4.1"], update=True, check=True)

        apk = package_manager.Apk(self)
        apk.install(["webkit2gtk-4.1-dev"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["webkitgtk3-devel"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["webkit2-gtk_41"], update=True, check=True)

    def package_info(self):
        PkgConfig(self, "webkit2gtk-4.1").fill_cpp_info(self.cpp_info, is_system=True)
