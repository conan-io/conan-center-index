import os

from conans import CMake, ConanFile, tools


class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, run_environment=True)
