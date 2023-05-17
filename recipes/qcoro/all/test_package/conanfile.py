from conan import ConanFile
from conan.tools.build import cross_building
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build_requirements(self):
        self.build_requires("cmake/3.23.2")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
