import os
import re
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.errors import ConanException


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.tool_requires("cmake/[>=3.20]")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # Check if the module file was generated
        # Check if the module file was generated
        pattern = re.compile(r"^conan_test_package\..*\.(so|dylib|pyd)$")
        found_file = None
        for filename in os.listdir(self.cpp.build.bindir):
            if pattern.match(filename):
                found_file = filename
                break

        if found_file:
            self.output.info(f"Found conan_test_package shared object: {found_file}")
        if not found_file:
            raise ConanException("conan_test_package shared object not found in bindir")

        if can_run(self):
            cmake = CMake(self)
            cmake.ctest(cli_args=["--verbose"])
