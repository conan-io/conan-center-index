import os

from conan import ConanFile, tools
from conans import CMake


class NcbiCxxToolkitTest(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run(os.path.join("bin", "basic_sample"),  run_environment=True)
            self.run(os.path.join("bin", "basic_sample2"), run_environment=True)
