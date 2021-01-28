import os

from conans import ConanFile, CMake, tools

class OatppLibresslTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "oatpp-libressl-test"), run_environment=True)
