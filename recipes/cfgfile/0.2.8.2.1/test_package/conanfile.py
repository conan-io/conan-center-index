from conans import ConanFile, CMake, tools
import os

class CfgfileTestConan(ConanFile):
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "cfgfile.test")
            self.run(bin_path, run_environment=True)
