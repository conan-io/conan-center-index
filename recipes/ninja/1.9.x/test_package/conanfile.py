from conans import ConanFile, tools
import os


class TestPackage(ConanFile):

    def test(self):
        if not tools.build.cross_building(self, self, skip_x64_x86=True):
            self.run("ninja --version", run_environment=True)
