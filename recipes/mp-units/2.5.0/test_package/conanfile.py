import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires("cmake/[>=4.2.1 <5]")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        opt = self.dependencies["mp-units"].options
        tc.cache_variables["MP_UNITS_BUILD_CXX_MODULES"] = opt.cxx_modules
        if opt.cxx_modules:
            tc.cache_variables["CMAKE_CXX_SCAN_FOR_MODULES"] = True
        if opt.import_std:
            tc.cache_variables["CMAKE_CXX_MODULE_STD"] = True
            # Current experimental support according to `Help/dev/experimental.rst`
            tc.cache_variables["CMAKE_EXPERIMENTAL_CXX_IMPORT_STD"] = (
                "d0edc3af-4c50-42ea-a356-e2862fe7a444"
            )
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package-headers")
            self.run(bin_path, env="conanrun")
