from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_CXX"] = self.dependencies["gmp"].options.enable_cxx
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = self.cpp.build.bindirs[0]
            self.run(os.path.join(bin_path, "test_package"), env="conanrun")
            if self.dependencies['gmp'].options.enable_cxx:
                self.run(os.path.join(bin_path, "test_package_cpp"), env="conanrun")
