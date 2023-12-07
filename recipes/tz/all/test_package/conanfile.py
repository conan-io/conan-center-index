from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.layout import basic_layout
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

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", check_type=str):
            self.tool_requires("msys2/cci.latest")

    def generate(self):
        # INFO: zdump does not consume TZDATA, need to pass absolute path of the zoneinfo directory
        self.tzdata = self.dependencies['tz'].runenv_info.vars(self).get('TZDATA')
        with open("tzdata.info", "w") as fd:
            fd.write(self.tzdata)

    def build(self):
        pass

    def test(self):
        if can_run(self):
            if self.dependencies['tz'].options.with_binary_db:
                self.output.info("Test that binary tzdb is readable")
                with open(os.path.join(self.generators_folder, "tzdata.info"), "r") as fd:
                    self.tzdata = fd.read()
                self.run(f"zdump {os.path.join(self.tzdata, 'America', 'Los_Angeles')}", env="conanrun")
            else:
                self.output.info("Test that source tzdb is readable")
                cmd = "python -c 'import os; tzdata = os.environ[\"TZDATA\"]; f=open(os.path.join(tzdata, \"factory\"), \"r\"); s = f.read(); f.close(); print(s)'"
                self.run(cmd, env="conanrun")
