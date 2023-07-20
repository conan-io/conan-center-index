import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._with_systemc_example:
            self.tool_requires("systemc/2.3.4")

    def layout(self):
        cmake_layout(self)

    @property
    def _with_systemc_example(self):
        # systemc is not available on Macos
        return not is_apple_os(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SYSTEMC"] = self._with_systemc_example
        tc.generate()

    def build(self):
        if can_run(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            verilator_path = os.path.join(self.dependencies["verilator"].package_folder, "bin", "verilator")
            self.run(f"perl {verilator_path} --version")
            bin_path = os.path.join(self.cpp.build.bindir, "blinky")
            self.run(bin_path, env="conanrun")
            if self._with_systemc_example:
                bin_path = os.path.join(self.cpp.build.bindir, "blinky_sc")
                self.run(bin_path, env="conanrun")
