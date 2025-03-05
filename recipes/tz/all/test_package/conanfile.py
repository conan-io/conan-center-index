from conan import ConanFile
from conan.tools.build import can_run
import os


class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self.settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.tool_requires("msys2/cci.latest")

    def test(self):
        if can_run(self):
            tzdata = self.dependencies.build['tz'].buildenv_info.vars(self).get('TZDATA')
            self.run(f"zdump {os.path.join(tzdata, 'America', 'Los_Angeles')}")
