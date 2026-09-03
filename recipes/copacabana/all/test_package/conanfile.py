import os

from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables={"COPACABANA_SOURCE": self.dependencies.build["copacabana"].package_folder})
        cmake.build()

    def test(self):
        pass
