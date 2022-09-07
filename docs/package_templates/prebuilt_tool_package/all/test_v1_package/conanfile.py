from conans import ConanFile
from conan.tools.build import cross_building


# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not cross_building(self):
            # self.run checks the command exit code
            # the tool must be available on PATH
            self.run("tool --version", run_environment=True)
