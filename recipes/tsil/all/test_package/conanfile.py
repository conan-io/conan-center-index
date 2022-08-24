import os

from conan import ConanFile, tools
from conans import CMake


class TsilTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake"]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
