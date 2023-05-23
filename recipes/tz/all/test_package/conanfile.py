from conan import ConanFile
from conan.tools.build import can_run


class TzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"
    tzdata = None

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

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
            self.run(f"zdump {self.tzdata}/America/Los_Angeles")
