import os

from conan import ConanFile
from conan.tools.build import can_run

from conans import CMake


class SdbusCppTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ("cmake", "cmake_find_package")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
