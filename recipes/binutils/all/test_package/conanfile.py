from conan import ConanFile
from conans import tools


class TestPackageConan(ConanFile):

    settings = "os"

    def test(self):
        if not tools.cross_building(self):
            self.run("as --version")
