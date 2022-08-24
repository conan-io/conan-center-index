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
            txt_name = os.path.join(self.source_folder, "test.txt")
            bin_path = os.path.join("bin", "test_package")
            self.run("{0} -encode -i {1}".format(bin_path, txt_name), run_environment=True)
