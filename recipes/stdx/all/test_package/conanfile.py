from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import can_run
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("gtest/1.15.0")
        
    def layout(self):
        cmake_layout(self)
        self.folders.build = "build"

    def generate(self):
        stdx_options = self.dependencies["stdx"].options
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_PREFIX_PATH"] = os.path.join(self.dependencies["stdx"].package_folder, "cmake").replace("\\", "/")
        tc.variables["STDX_ENABLE_FLAG"] = "ON" if stdx_options.enable_flag else "OFF"
        tc.variables["STDX_ENABLE_LOGGER"] = "ON" if stdx_options.enable_logger else "OFF"
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            stdx_options = self.dependencies["stdx"].options
            if stdx_options.enable_logger:
                self.run(os.path.join(self.cpp.build.bindir, "test_logger"), env="conanrun")
            if stdx_options.enable_flag:
                self.run(os.path.join(self.cpp.build.bindir, "test_flag"), env="conanrun")
