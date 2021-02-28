import sys

from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        version_str = next(iter(self.requires.values())).ref.version
        cmake = CMake(self)
        cmake.definitions["CMAKE_CXX_STANDARD"] = "11" if version_str == "0.17.6" else "17"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
