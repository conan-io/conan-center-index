from conans import ConanFile, tools


class KcovTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("kcov --version", run_environment=True)
