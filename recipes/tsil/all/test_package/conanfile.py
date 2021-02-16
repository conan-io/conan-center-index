import os

from conans import ConanFile, CMake, tools


class TsilTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake"]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
