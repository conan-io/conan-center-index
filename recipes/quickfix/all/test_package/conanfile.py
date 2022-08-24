import os

from conan import ConanFile, tools
from conan.tools.cmake import CMake


class QuickfixTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "executor")
            self.run(bin_path, run_environment=True)
