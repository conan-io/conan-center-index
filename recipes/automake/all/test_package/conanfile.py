from os import environ

from conan import ConanFile
from conan.tools.build import can_run

required_conan_version = ">=1.50.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv"
    test_type = "explicit"
    win_bash = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not environ.get("CONAN_BASH_PATH"):
            self.tool_requires("msys2/cci.latest")

    def build(self):
        pass

    def test(self):
        if can_run(self):
            self.run("automake --version", run_environment=True, env="conanbuild", win_bash=self.settings.os == "Windows")
