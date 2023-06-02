from conan import ConanFile
from conan.tools.build import can_run, valid_min_cppstd
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type",
    generators = "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    @property
    def _min_cppstd(self):
        return 11

    def generate(self):
        tc = CMakeToolchain(self)
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
