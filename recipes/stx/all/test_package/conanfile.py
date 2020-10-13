from conans import ConanFile, CMake, tools
import os

class STXTestConan(ConanFile):
    settings = 'os', 'compiler', 'build_type', 'arch'
    generators = 'cmake', 'cmake_find_package'

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join('bin', 'example_basic'), run_environment=True)
            self.run(os.path.join('bin', 'example_find_package'), run_environment=True)
