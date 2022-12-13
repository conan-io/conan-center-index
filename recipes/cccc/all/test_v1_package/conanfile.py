import os
from conans import ConanFile, CMake
from conan.tools import build

class CCCCTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake", "cmake_find_package_multi"]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # the cmake file shall error if cccc not present
        pass
