import os
from conans import ConanFile, CMake
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package_multi", "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run(os.path.join("bin","test_package"), run_environment=True)
