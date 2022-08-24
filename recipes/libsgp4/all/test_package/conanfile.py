import os

from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            tle_name = os.path.join(self.source_folder, "SGP4-VER.TLE")
            bin_path = os.path.join("bin", "test_package")
            self.run("{0} {1}".format(bin_path, tle_name), run_environment=True)
