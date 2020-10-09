from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    settings = "os", "os_build"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("ragel --version")
