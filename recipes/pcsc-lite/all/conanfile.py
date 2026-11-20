from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.system import package_manager
from conan.tools.gnu import PkgConfig

required_conan_version = ">=2.0.9"


class PcscLiteSystemConan(ConanFile):
    name = "pcsc-lite"
    version = "system"
    description = "Middleware to access a smart card using SCard API (PC/SC)."
    topics = ("apdu", "pcsc-lite", "smartcard")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pcsclite.apdu.fr/"
    license = "BSD-3-Clause"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("pcsc-lite is only for Linux and FreeBSD.")

    def package_id(self):
        self.info.clear()

    def system_requirements(self):
        dnf = package_manager.Dnf(self)
        dnf.install(["pcsc-lite-devel"], update=True, check=True)

        yum = package_manager.Yum(self)
        yum.install(["pcsc-lite-devel"], update=True, check=True)

        apt = package_manager.Apt(self)
        apt.install(["libpcsclite-dev"], update=True, check=True)

        pacman = package_manager.PacMan(self)
        pacman.install(["pcsclite"], update=True, check=True)

        zypper = package_manager.Zypper(self)
        zypper.install(["pcsc-lite-devel"], update=True, check=True)

        apk = package_manager.Apk(self)
        apk.install(["pcsc-lite-dev"], update=True, check=True)

        pkg = package_manager.Pkg(self)
        pkg.install(["pcsc-lite"], update=True, check=True)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("pkg_config_name", "libpcsclite")
        pkg_config = PkgConfig(self, "libpcsclite")
        pkg_config.fill_cpp_info(self.cpp_info)
        self.cpp_info.set_property("system_package_version", str(pkg_config.version))