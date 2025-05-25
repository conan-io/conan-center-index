import os
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.errors import ConanException

class TestSuiteSparseConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = self.cpp.build.bindirs[0]
        exe = os.path.join(bin_path, "test_package")
        if not os.path.exists(exe):
            raise ConanException(f"Not found test_package in {bin_path}")
        self.run(exe, env="conanrun")
