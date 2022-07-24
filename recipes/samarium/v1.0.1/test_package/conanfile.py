import os

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.abspath("test_package")
            self.run(bin_path, run_environment=True)
