from conan import ConanFile, tools
from conans import CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            font_path = os.path.join(self.source_folder, "OpenSans-Bold.ttf")
            self.run("{} {}".format(bin_path, font_path), run_environment=True)
