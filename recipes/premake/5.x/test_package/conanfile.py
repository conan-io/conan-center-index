from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("premake5 --version", run_environment=True)
