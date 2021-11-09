from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def test(self):
        if not tools.cross_building(self):
            self.run("xqilla -h")
