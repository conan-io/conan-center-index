import os

from conans import ConanFile, CMake, tools


class NsyncTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            os.chdir("bin")
            self.run(".%sexample_c" % os.sep)
            self.run(".%sexample_cpp" % os.sep)
