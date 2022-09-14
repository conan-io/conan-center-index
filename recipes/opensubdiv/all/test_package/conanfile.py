import os

from conans import ConanFile, CMake
from conan.tools.build import cross_building


class USDTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
