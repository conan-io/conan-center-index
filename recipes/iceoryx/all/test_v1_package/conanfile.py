import os
import os.path
from conans import ConanFile, CMake

class IceoryxTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake", "cmake_find_package_multi"]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
        if can_run(self):
            self.run(bin_path, env="conanrun")
