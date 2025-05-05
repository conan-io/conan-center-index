from conans import ConanFile, tools


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self):
            self.run("7za", run_environment=True)
