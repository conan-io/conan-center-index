from conan import ConanFile
from conan.tools.build import can_run
import os


class CcclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VCVars", "VirtualBuildEnv"
    test_type = "explicit"
    win_bash = True

    @property
    def _settings_build(self):
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")

    def build(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            return  # cccl needs a bash if there isn't a bash we can't build
        cxx = "cccl "
        src = os.path.join(self.source_folder, "example.cpp").replace("\\", "/")
        self.run(f"{cxx} {src} -o example", cwd=self.build_folder)

    def test(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            return  # cccl needs a bash if there isn't a bash we can't build
        if can_run(self):
            self.run("./example") #test self.run still runs in bash, so it needs "./"; seems weird but okay...
