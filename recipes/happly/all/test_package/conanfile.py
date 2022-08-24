import glob
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
            self.run(os.path.join("bin", "test_package"))
            # Let's check if the *.ply file has been created successfully
            ply_format_file = glob.glob("*.ply")[0]
            assert os.path.exists(ply_format_file)
