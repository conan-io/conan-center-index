import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        opt = self.dependencies["mp-units"].options
        if opt.cxx_modules:
            tc.cache_variables["CMAKE_CXX_SCAN_FOR_MODULES"] = True
        if opt.import_std:
            tc.cache_variables["CMAKE_CXX_MODULE_STD"] = True
            # Current experimental support according to `Help/dev/experimental.rst`
            tc.cache_variables[
                "CMAKE_EXPERIMENTAL_CXX_IMPORT_STD"
            ] = "0e5b6991-d74f-4b3d-a41c-cf096e0b2508"
        # TODO remove the below when Conan will learn to handle C++ modules
        if opt.freestanding:
            tc.cache_variables["MP_UNITS_API_FREESTANDING"] = True
        else:
            tc.cache_variables["MP_UNITS_API_STD_FORMAT"] = opt.std_format
        tc.cache_variables["MP_UNITS_API_CONTRACTS"] = str(opt.contracts).upper()
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
