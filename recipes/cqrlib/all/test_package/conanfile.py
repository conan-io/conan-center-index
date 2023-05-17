from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path_c = os.path.join(self.cpp.build.bindirs[0], "test_package_c")
            self.run(bin_path_c, env="conanrun")
            bin_path_cpp = os.path.join(self.cpp.build.bindirs[0], "test_package_cpp")
            self.run(bin_path_cpp, env="conanrun")
