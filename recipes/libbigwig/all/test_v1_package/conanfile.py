import os

from conan.tools.build import cross_building
from conans import CMake, ConanFile


class TestPackageConan(ConanFile):
    settings = "arch", "build_type", "compiler", "os"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
