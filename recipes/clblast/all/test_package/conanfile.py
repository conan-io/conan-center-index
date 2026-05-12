import os
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run


class clblastTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.test_requires(self.tested_reference_str)
        self.requires("opencl-clhpp-headers/2025.07.22")
        if self.settings.os != "Macos":
            self.requires("opencl-icd-loader/2025.07.22", options={"shared": True})

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "example")
            self.run(bin_path, env="conanrun")
