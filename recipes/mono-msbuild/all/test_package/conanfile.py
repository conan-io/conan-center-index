from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    #generators = "cmake"

    def build(self):
        pass

    def test(self):
        if not tools.cross_building(self):
            self.run("msbuild --version", run_environment=True)
