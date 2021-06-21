from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "cmake", "cmake_find_package"
    
    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            cmake = CMake(self)
            cmake.configure()
            cmake.build(target="flatbuffers")
        
    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            self.run("flatc --version", run_environment=True)
            self.run("flathash fnv1_16 conan", run_environment=True)
