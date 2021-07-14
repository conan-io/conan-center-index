from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os"

    def test(self):
        if tools.cross_building(self.settings):
            return
        self.run("bloaty --version", run_environment=True)
