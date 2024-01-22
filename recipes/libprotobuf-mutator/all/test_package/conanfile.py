from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)
        self.requires("protobuf/3.21.12")

    def layout(self):
        cmake_layout(self)

    def build_requirements(self):
        self.tool_requires("protobuf/<host_version>")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_VERBOSE_MAKEFILE"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
