from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = ("os", "arch", "compiler", "build_type")
    generators = ("cmake", "cmake_find_package_multi")
    test_type = "explicit"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
