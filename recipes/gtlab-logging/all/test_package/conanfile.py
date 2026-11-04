from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import can_run
import os


class GTlabLoggingTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"

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
            bin_path = os.path.join(self.cpp.build.bindirs[0], "example")
            self.run(bin_path, env="conanrun")
