from conans import ConanFile, CMake, tools
import os

class CfgfileTestConan(ConanFile):
    generators = "cmake", "cmake_find_package"

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def build_requirements(self):
        if hasattr(self, "settings_build"):
            self.build_requires(str(self.requires["cfgfile"]))

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "cfgfile.test")
            cfg_path = os.path.join(self.source_folder, "test.cfg");
            self.run("{} \"{}\"".format(bin_path, cfg_path), run_environment=True)
