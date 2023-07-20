import os

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run, cross_building
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.files import mkdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join(self.dependencies["flatcc"].package_folder, "bin", "flatcc")
        if not os.path.isfile(bin_path) or not os.access(bin_path, os.X_OK):
            raise ConanException("flatcc doesn't exist.")
        if can_run(self):
            self.run("flatcc --version")
            bin_path = os.path.join(self.cpp.build.bindir, "monster")
            self.run(bin_path, env="conanrun")
