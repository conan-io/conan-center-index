from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run("gperf --version", run_environment=True)
