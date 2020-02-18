import os

from conans import ConanFile, CMake, tools


class TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        self.copy("*.dylib*", dst="bin", src="lib")
    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(".%sexample" % os.sep)
