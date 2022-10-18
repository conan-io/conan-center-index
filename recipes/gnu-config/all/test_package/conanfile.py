from conan import ConanFile
from conan.errors import ConanException
from conans import tools as tools_legacy


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                self.tool_requires("msys2/cci.latest")

    def test(self):
        triplet = tools_legacy.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))
        self.run("config.guess")
        try:
            self.run(f"config.sub {triplet}")
        except ConanException:
            self.output.info("Current configuration is not supported by GNU config.\nIgnoring...")
