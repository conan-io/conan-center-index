from conan import ConanFile, tools
from conans import CMake
import os

class ArgsParserTestConan(ConanFile):
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "args-parser.test")
            self.run(bin_path, run_environment=True)
