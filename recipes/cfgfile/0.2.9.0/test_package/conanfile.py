from conans import ConanFile, CMake, tools
import os

class CfgfileTestConan(ConanFile):
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "cfgfile.test")
            cfg_path = os.path.join(self.source_folder, "test.cfg");
            self.run("{} \"{}\"".format(bin_path, cfg_path), run_environment=True)
