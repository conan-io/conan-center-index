from conan import ConanFile, tools
from conans import CMake
import os


class LibvaultTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            self.run(os.path.join("bin", "example"), run_environment=True)
