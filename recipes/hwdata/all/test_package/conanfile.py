import os

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfig, PkgConfigDeps
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("meson/1.2.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()

        pkg_config = PkgConfig(self, "hwdata", self.generators_folder)
        pkgdatadir = pkg_config.variables["pkgdatadir"]
        expected_pkgdatadir = os.path.join(self.dependencies.direct_host[self.tested_reference_str].cpp_info.resdirs[0], self.dependencies.direct_host[self.tested_reference_str].ref.name)
        if pkgdatadir != expected_pkgdatadir:
            raise ConanException(f"The pkg_config variable pkgdatadir is '{pkgdatadir}' but should be '{expected_pkgdatadir}'")

        meson_toolchain = MesonToolchain(self)
        meson_toolchain.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()

    def test(self):
        pass
