from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            font = os.path.join(self.source_folder, "example.ttf")
            bin_path = os.path.join("bin", "test_package")
            self.run("{} {}".format(bin_path, font), run_environment=True)

