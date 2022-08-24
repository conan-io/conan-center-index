import os

from conan import ConanFile, tools
from conan.tools.cmake import CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            glb_path = os.path.join(self.source_folder, "box01.glb")
            bin_path = os.path.join("bin", "test_package")
            self.run("{0} {1}".format(bin_path, glb_path), run_environment=True)
