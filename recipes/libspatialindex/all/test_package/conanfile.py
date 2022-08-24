import os

from conan import ConanFile, tools
from conans import CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            bin_path_c = os.path.join("bin", "test_package_c")
            self.run(bin_path_c, run_environment=True)
            bin_path_cpp = os.path.join("bin", "test_package_cpp")
            self.run(bin_path_cpp, run_environment=True)
