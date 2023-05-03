from conan import ConanFile
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake
from conan.tools.build.cross_building import cross_building
from conan.tools.cmake.layout import cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.build_requires("cmake/[>=3.21.3 <4.0.0]")
        self.build_requires("ninja/[>=1.10.0 <2.0.0]")

    def generate(self):
        deps = CMakeDeps(self)
        deps.check_components_exist = True
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self, self.settings):
            self.run("./test_package")
