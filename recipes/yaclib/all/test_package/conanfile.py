from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os

class TestPackageConan(ConanFile):
    test_type = 'explicit'
    generators = 'CMakeDeps', 'VirtualRunEnv'
    settings = 'os', 'arch', 'compiler', 'build_type'

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['YACLIB_CORO'] = self.dependencies["yaclib"].options.coro
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], 'test_package')
            self.run(bin_path, env="conanrun")
