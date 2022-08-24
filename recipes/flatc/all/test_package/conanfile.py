from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "cmake", "cmake_find_package"
    
    def build_requirements(self):
        if tools.build.cross_building(self, self.settings):
            self.build_requires(str(self.requires["flatc"]))
        
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="flatbuffers")
        
    def test(self):
        if not tools.build.cross_building(self, self, skip_x64_x86=True):
            self.run("flatc --version", run_environment=True)
            self.run("flathash fnv1_16 conan", run_environment=True)
