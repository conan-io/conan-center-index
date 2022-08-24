import os
from conan import ConanFile, tools


class TestPackageConan(ConanFile):

    settings = "os", "arch"

    def test(self):
        if not tools.build.cross_building(self, self):
            self.output.info("Node version:")
            self.run("node --version", run_environment=True)
