from conans import ConanFile, tools


class TestPackage(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("7zDec", run_environment=True)
            self.run("lzma", run_environment=True)
