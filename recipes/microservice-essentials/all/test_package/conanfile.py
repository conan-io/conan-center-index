from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan import ConanFile
from conan.tools.build import cross_building
import os

class TestTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"    

    def build(self):
        cmake = CMake(self)        
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):            
            self.run(".%stest" % os.sep)
