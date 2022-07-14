import os
from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self):
            self.run("echo $LD", run_environment=True)
            self.run("mold -v", run_environment=True)
