from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps"

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
            bin_path_c = os.path.join(self.cpp.build.bindir, "test_package_c")
            self.run(bin_path_c, env="conanrun")
            bin_path_cpp = os.path.join(self.cpp.build.bindir, "test_package_cpp")
            if os.path.exists(bin_path_cpp):
                self.run(bin_path_cpp, env="conanrun")
