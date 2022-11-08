from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.env import Environment
import os


class CcclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VCVars"
    
    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not Environment().vars(self).get("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def build(self):
        if can_run(self):
            cxx = "sh cccl "
            src = os.path.join(self.source_folder, "example.cpp")
            self.run(f"{cxx} {src} -o example", win_bash=self.settings.os is "Windows", run_environment=True)

    def test(self):
        if can_run(self):
            self.run(os.path.join(self.build_folder, "example"))
