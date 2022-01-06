import os

from conans import ConanFile, CMake, tools


class DaggyTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_paths", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')

    def test(self):
        if not tools.cross_building(self.settings):
            os.chdir("bin")
            self.run(".%stestcpp" % os.sep)
            self.run(".%stestc" % os.sep)