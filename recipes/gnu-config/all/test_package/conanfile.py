from conans import ConanFile, tools
from conans.errors import ConanException


class TestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20190524")

    def test(self):
        triplet = tools.get_gnu_triplet(str(self.settings.os), str(self.settings.arch), str(self.settings.compiler))
        self.run("config.guess", run_environment=True, win_bash=tools.os_info.is_windows)
        try:
            self.run("config.sub {}".format(triplet), run_environment=True, win_bash=tools.os_info.is_windows)
        except ConanException:
            self.output.info("Current configuration is not supported by GNU config.\nIgnoring...")
