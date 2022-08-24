from conan import ConanFile, tools


class KcovTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            self.run("kcov --version", run_environment=True)
