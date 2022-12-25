from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


class LibhalTestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ("cmake", "cmake_find_package_multi")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if cross_building(self):
            bin_path = os.path.join(self.build_folder, "bin", "test_package")
            self.run(bin_path, run_environment=True)
