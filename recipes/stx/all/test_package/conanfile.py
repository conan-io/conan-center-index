from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class STXTestConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'
    generators = 'cmake', 'cmake_find_package_multi'

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join('bin', 'example'), run_environment=True)
