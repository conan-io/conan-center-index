from conan import ConanFile, tools
from conans.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def test(self):
        triplet = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))
        self.run("config.guess", run_environment=True, win_bash=tools.os_info.is_windows)
        try:
            self.run("config.sub {}".format(triplet), run_environment=True, win_bash=tools.os_info.is_windows)
        except ConanException:
            self.output.info("Current configuration is not supported by GNU config.\nIgnoring...")
