import os

from conan import ConanFile, tools
from conans import CMake

class OatppLibresslTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run(os.path.join("bin", "oatpp-libressl-test"), run_environment=True)
