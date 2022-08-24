from conan import ConanFile, tools
from conans import CMake
import os

class ReadExcelTestConan(ConanFile):
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "read-excel.test")
            xls_path = os.path.join(self.source_folder, "sample.xls");
            self.run("{} \"{}\"".format(bin_path, xls_path), run_environment=True)
