import os

from conans import ConanFile, CMake, tools


class IceoryxTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake","cmake_find_package_multi"]

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package"
        cmake.configure()
        cmake.build()

    def test(self):
        path, dirs, files = next(os.walk("bin"))
        assert len(files) == 19
        print("All %d example files are present" % (len(files)))
