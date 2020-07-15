import os

from conans import ConanFile, CMake, tools
import pathlib

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            os.chdir("bin")
            file = os.path.join( pathlib.Path(__file__).parent.absolute(), "tng_example.tng")
            self.run(".%stest_package %s" % (os.sep, file) )
