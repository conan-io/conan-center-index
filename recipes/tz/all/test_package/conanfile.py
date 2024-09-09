from conan import ConanFile
from conan.tools.build import can_run
from conan.errors import ConanException
import os


class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"
    tzdata = None

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.tool_requires("msys2/cci.latest")

    def generate(self):
        # INFO: zdump does not consume TZDATA, need to pass absolute path of the zoneinfo directory
        self.tzdata = self.dependencies.build['tz'].buildenv_info.vars(self).get('TZDATA')
        with open("tzdata.info", "w") as fd:
            fd.write(self.tzdata)

    def build(self):
        pass

    def test(self):
        if can_run(self):
            with open("tzdata.info", "r") as fd:
                self.tzdata = fd.read()
            self.run(f"zdump {os.path.join(self.tzdata, 'America', 'Los_Angeles')}")
