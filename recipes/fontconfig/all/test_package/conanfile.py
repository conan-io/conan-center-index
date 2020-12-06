import os
from conans import ConanFile, CMake, tools

class FontconfigTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run(os.path.join("bin", "example"), run_environment=True)
