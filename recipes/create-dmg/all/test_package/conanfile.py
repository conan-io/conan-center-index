from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os"

    def test(self):
        if not tools.cross_building(self):
            self.run("create-dmg --version", run_environment=True)
