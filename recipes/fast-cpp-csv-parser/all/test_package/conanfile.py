import os

from conan import ConanFile, tools
from conans import CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            csv_name = os.path.join(self.source_folder, "test_package.csv")
            bin_path = os.path.join("bin", "test_package")
            self.run("{0} {1}".format(bin_path, csv_name), run_environment=True)
