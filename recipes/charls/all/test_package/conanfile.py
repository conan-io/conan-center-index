from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_c_path = os.path.join(self.cpp.build.bindirs[0], "test_package_c")
            self.run(bin_c_path, env="conanrun")
            bin_cpp_path = os.path.join(self.cpp.build.bindirs[0], "test_package_cpp")
            self.run(bin_cpp_path, env="conanrun")
