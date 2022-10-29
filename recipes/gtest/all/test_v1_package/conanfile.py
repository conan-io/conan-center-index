import os

from conan.tools.build import cross_building
from conans import ConanFile, CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions['WITH_GMOCK'] = self.options['gtest'].build_gmock
        cmake.definitions['WITH_MAIN'] = not self.options['gtest'].no_main
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
