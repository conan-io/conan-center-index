import os

from conans import ConanFile, CMake, tools


class KcovTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake"]

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("kcov --version", run_environment=True)
