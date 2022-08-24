import os

from conan import ConanFile, tools
from conans import CMake


class OatppSwaggerTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
           self.run(os.path.join("bin", "test_package"), run_environment=True)
