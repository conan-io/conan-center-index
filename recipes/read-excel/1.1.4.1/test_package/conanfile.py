from conans import ConanFile, CMake, tools
import os

class ReadExcelTestConan(ConanFile):
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "read-excel.test")
            self.run(bin_path, run_environment=True)
