import os

from conan import ConanFile, tools
from conans import CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            txt_name = os.path.join(self.source_folder, "test.txt")
            bin_path = os.path.join("bin", "test_package")
            self.run("{0} -encode -i {1}".format(bin_path, txt_name), run_environment=True)
