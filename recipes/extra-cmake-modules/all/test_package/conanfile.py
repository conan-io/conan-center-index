from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import can_run
import os

class ExtraCMakeModulesTestConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"

    def build_requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            runpath = os.path.join(self.cpp.build.bindir, "example")
            self.run(runpath, env="conanrun")
