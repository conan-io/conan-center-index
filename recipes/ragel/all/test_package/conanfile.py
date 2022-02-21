from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    settings = "os", "arch", "build_type", "compiler"

    def test(self):
        if not tools.cross_building(self):
            self.run("ragel --version", run_environment=True)
