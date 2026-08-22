from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINYSPLINE_CXX"] = self.dependencies["tinyspline"].options.cxx
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_c_path = os.path.join(self.cpp.build.bindir, "test_package_c")
            self.run(bin_c_path, env="conanrun")

            if self.dependencies["tinyspline"].options.cxx:
                bin_cpp_path = os.path.join(self.cpp.build.bindir, "test_package_cpp")
                self.run(bin_cpp_path, env="conanrun")
