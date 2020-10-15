import os
from conans import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.build import cross_building as tools_cross_building
from conan.tools.layout import cmake_layout

required_conan_version = ">=1.43.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools_cross_building(self):
            self.run(os.path.join(self.cpp.build.bindirs[0], "example"), run_environment=True)
