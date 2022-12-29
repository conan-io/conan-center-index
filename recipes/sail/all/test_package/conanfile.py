from conan.tools.build import cross_building
from conans import ConanFile, CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package_c")
            self.run(bin_path, run_environment=True)

            bin_path = os.path.join("bin", "test_package_cxx")
            self.run(bin_path, run_environment=True)
