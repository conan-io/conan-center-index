from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "cmake", "cmake_find_package"
    
    def build_requirements(self):
        if tools.cross_building(self.settings):
            self.build_requires(str(self.requires["flatc"]))
        
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="flatbuffers")
        
    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("flatc --version", run_environment=True)
            self.run("flathash fnv1_16 conan", run_environment=True)
