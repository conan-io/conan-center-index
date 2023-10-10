import os

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfig, PkgConfigDeps
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def generate(self):
        pkg_config_deps = PkgConfigDeps(self)
        if self._settings_build:
            pkg_config_deps.build_context_activated = ["hwdata"]
        pkg_config_deps.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()

    def build(self):
        pkg_config = PkgConfig(self, "hwdata", self.generators_folder)
        self.output.info(pkg_config.variables["pkgdatadir"])
        assert len(pkg_config.variables["pkgdatadir"]) > 0

    def test(self):
        pass
