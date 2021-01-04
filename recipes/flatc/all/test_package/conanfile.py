from conans import ConanFile, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch"
    generators = "cmake", "cmake_find_package"
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="flatbuffers")
        
    def test(self):
        self.run("flatc --version", run_environment=True)
        self.run("flathash fnv1_16 conan", run_environment=True)
