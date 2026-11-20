import os
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run


class TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)
        # improc's public headers expose opencv2 types; consumers must find OpenCV.
        # For shared-library builds CMakeDeps does not propagate transitive deps'
        # cmake configs, so we declare it here so CMakeDeps generates the files.
        self.requires("opencv/4.10.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.15 <4]")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(os.path.join(self.cpp.build.bindir, "test_package"))
