from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("gperf --version")
