import os

from conan import ConanFile, tools
from conans import CMake


class QuickfixTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "executor")
            self.run(bin_path, run_environment=True)
