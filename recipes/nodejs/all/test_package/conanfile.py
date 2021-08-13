import os
from conans import ConanFile, tools


class TestPackageConan(ConanFile):

    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self):
            self.output.info("Node version:")
            self.run("node --version", run_environment=True)
