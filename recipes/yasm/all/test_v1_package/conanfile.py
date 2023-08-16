from conans import ConanFile
from conan.tools.build import cross_building


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not cross_building(self):
            self.run("yasm --help", run_environment=True)
