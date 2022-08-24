from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            bin_path = os.path.join("bin", "test_package")
            bees = os.path.join(self.source_folder, "atlas_small_4x4.astc")
            self.run("{} {} 256 256".format(bin_path, bees), run_environment=True)
