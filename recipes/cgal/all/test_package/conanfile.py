import os

from conan import ConanFile
from conan.tools import build
from conans import CMake


class TestPackageConan(ConanFile):
    name="test_package_cgal"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not build.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
