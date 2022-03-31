from conans import ConanFile, tools
import sys


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("uncrustify --version", run_environment=True)
