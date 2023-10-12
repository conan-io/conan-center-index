import os

from conan.tools.build import cross_building
from conan.tools.cmake import CMake, cmake_layout
from conans.model.conan_file import ConanFile


class AwsSdkCppTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(self.build_folder, "example")
            self.run(bin_path)
