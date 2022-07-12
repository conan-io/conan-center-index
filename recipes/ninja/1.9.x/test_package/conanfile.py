from conans import ConanFile, tools
import os


class TestPackage(ConanFile):

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("ninja --version", run_environment=True)
