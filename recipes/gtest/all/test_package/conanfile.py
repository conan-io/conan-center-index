import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)

        with_gmock = bool(self.dependencies[self.tested_reference_str].options.build_gmock)
        tc.cache_variables['WITH_GMOCK'] = with_gmock
        tc.preprocessor_definitions['WITH_GMOCK'] = with_gmock

        with_main = not self.dependencies[self.tested_reference_str].options.no_main
        tc.cache_variables['WITH_MAIN'] = with_main
        tc.preprocessor_definitions['WITH_MAIN'] = with_main

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
