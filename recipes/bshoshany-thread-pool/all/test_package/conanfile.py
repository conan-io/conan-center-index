import os
from conan import ConanFile, tools
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "arch", "build_type", "compiler", "os"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
