import os
import re
from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        pattern = re.compile(r"^test_module\..*\.(so|dylib|dll)$")
        for filename in os.listdir(self.cpp.build.bindir):
            if pattern.match(filename):
                print("Found test_module shared object:", filename)
                return
        raise FileNotFoundError("test_module shared object not found in bindir")
