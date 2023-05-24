from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.scm import Version
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        version = tools.Version(self.deps_cpp_info["openimageio"].version)

        tc = CMakeToolchain(self)
        tc.variables["CMAKE_CXX_STANDARD"] = 14 if version >= "2.3.0.0" else 11
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
