from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("jwasm -h", run_environment=True)
