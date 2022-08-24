import os

from conan import ConanFile, tools
from conans import CMake


class LibargsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run("{} --sum 1000 700 1".format(bin_path),
                     run_environment=True)
