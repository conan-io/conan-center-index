from conan import ConanFile
from conan.tools import build
from conan.tools.cmake import CMake

import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not build.cross_building(self):
            font = os.path.join(self.source_folder, "example.ttf")
            bin_path = os.path.join(self.build_folder, "test_package")
            self.run("{} {}".format(bin_path, font), run_environment=True)

