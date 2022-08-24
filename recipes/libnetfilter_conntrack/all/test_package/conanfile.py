import os

from conan import ConanFile, tools
from conans import CMake

class Libnetfilter_conntrackTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "example")
            self.run("{} {}".format(bin_path, 0), run_environment=True)
