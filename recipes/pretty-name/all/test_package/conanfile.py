import os
from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        self.cmake = CMake(self)
        self.cmake.configure()
        self.cmake.build()

    def build_requirements(self):
        self.build_requires("cmake/3.18.0")

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
