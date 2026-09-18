import os
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        opts = self.dependencies[self.tested_reference_str].options
        tc.variables["FMT_HEADER_ONLY"] = opts.header_only
        if opts.get_safe("with_module"):
            tc.cache_variables["FMT_TEST_USE_MODULE"] = True
            tc.generator = "Ninja"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(os.path.join(self.cpp.build.bindirs[0], "test_package"), env="conanrun")
            self.run(os.path.join(self.cpp.build.bindirs[0], "test_ranges"), env="conanrun")
