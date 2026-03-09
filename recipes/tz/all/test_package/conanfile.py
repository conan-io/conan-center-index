from conan import ConanFile
from conan.tools.build import can_run
import io


class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def test(self):
        if can_run(self):
            stdout = io.StringIO()
            self.run("zdump --help", env="conanrun", stdout=stdout)
