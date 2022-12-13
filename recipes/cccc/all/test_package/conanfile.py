import os
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run

class CCCCTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # the cmake file shall error if cccc not present
        pass
