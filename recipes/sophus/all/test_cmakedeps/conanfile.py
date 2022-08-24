import os
from conan import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain
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
        if not tools.build.cross_building(self, self):
            self.run(os.path.join(self.cpp.build.bindirs[0], "test_package"), run_environment=True)
