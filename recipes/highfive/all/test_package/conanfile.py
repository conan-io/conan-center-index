from conan import ConanFile, tools
from conans import CMake
import os.path


class HighFiveTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
