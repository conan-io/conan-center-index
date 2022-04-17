import os

from conan import ConanFile
from conan.tools.cmake import (
    CMakeToolchain,
    CMakeDeps,
    CMake
)
from conan.tools.build import cross_building


class PclTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_VERBOSE_MAKEFILE"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(".", "pcl_test_package")
            self.run(bin_path, run_environment=True)
