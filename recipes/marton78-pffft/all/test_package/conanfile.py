from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        opts = self.dependencies[self.tested_reference_str].options
        tc = CMakeToolchain(self)
        tc.cache_variables["PFFFT_WITH_FLOAT"] = bool(opts.with_float)
        tc.cache_variables["PFFFT_WITH_PFFASTCONV"] = bool(opts.with_pffastconv)
        tc.cache_variables["PFFFT_WITH_PFDSP"] = bool(opts.with_pfdsp)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
