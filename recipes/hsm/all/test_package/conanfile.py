import os

from conans import ConanFile, CMake, tools


class HsmTestConan(ConanFile):
    settings = "cppstd", "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()


    def test(self):
        if not tools.cross_building(self):
            os.chdir("bin")
            self.run(".%sexample" % os.sep, run_environment=True)
