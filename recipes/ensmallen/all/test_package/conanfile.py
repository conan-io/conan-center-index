import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run

class ensmallenTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)
        # Required for consumers of armadillo>=12.2.0 due to upstream changes
        # and armadillo/*:use_hdf5=True by default.
        # See https://github.com/conan-io/conan-center-index/pull/17320 for more
        # information.
        self.requires("hdf5/1.14.1")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if can_run(self):
            cmd = [os.path.join(self.cpp.build.bindir, "example"), "10", "20"]
            self.run(" ".join(cmd), env="conanrun")
