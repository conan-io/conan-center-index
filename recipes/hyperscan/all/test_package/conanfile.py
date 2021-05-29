import os

from conans import ConanFile, CMake, tools


class HyperscanTestConan(ConanFile):
    settings = "os", "build_type", "arch", "compiler"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
