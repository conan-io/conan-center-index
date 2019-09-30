from conans import ConanFile, CMake
import os


class TestPackageConan(ConanFile):
    name = "test_package"
    generators = "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run(".{}{}".format(os.sep, self.name))
