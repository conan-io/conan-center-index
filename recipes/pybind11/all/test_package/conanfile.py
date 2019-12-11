from conans import ConanFile, CMake
import os
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("{} {} {}".format(sys.executable,
                                   os.path.join(self.source_folder, "test.py"),
                                   os.path.join(self.build_folder, "lib")), run_environment=True)
