import os

from conans import ConanFile, CMake, tools
from conan.tools.build import cross_building


class HexlTestConan(ConanFile):
    settings = "os", "build_type", "arch", "compiler"
    generators = "cmake", "cmake_find_package"


    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
