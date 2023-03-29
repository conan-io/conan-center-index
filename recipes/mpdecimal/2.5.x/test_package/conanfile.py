import os
import pathlib
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        build_type = self.settings.build_type.value
        tc = CMakeToolchain(self)
        tc.variables["MPDECIMAL_CXX"] = self.dependencies["mpdecimal"].options.cxx
        tc.variables[f"CMAKE_RUNTIME_OUTPUT_DIRECTORY_{build_type.upper()}"] = "bin"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = pathlib.Path(self.cpp.build.bindirs[0], "bin", "test_package")
            self.run("{} 13 100".format(bin_path), env="conanrun")
            if self.options["mpdecimal"].cxx:
                bin_path = pathlib.Path(self.cpp.build.bindirs[0], "bin", "test_package_cpp")
                self.run("{} 13 100".format(bin_path), env="conanrun")
