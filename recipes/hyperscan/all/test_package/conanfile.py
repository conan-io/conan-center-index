import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import can_run

class HyperscanTestConan(ConanFile):
    settings = "os", "build_type", "arch", "compiler"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_CHIMERA"] = self.options["hyperscan"].build_chimera
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "hs_example")
            self.run(bin_path, env="conanrun")

            if self.options["hyperscan"].build_chimera:
                bin_path = os.path.join(self.cpp.build.bindirs[0], "ch_example")
                self.run(bin_path, env="conanrun")
