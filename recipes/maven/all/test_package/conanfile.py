from conans import ConanFile, tools


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler"

    def build(self):
        pass

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("mvn --version")
