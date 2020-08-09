import os
from conans import ConanFile, CMake, RunEnvironment, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        with tools.environment_append(RunEnvironment(self).vars):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test")
            self.run(bin_path, run_environment=True)

