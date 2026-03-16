from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy, get
import os

class AkashaConan(ConanFile):
    name = "akasha"
    version = "1.0.0"
    description = "High-performance hierarchical data store with memory-mapped file persistence"
    url = "https://github.com/yawin123/Akasha"
    license = "MIT"
    topics = ("libraries", "cpp", "data-store", "memory-mapped")
    
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "build_examples": [True, False],
        "build_single_archive": [True, False],
    }
    default_options = {
        "build_examples": False,
        "build_single_archive": False,
    }
    
    generators = "CMakeDeps", "CMakeToolchain"
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
    
    def requirements(self):
        self.requires("boost/1.90.0")
    
    def layout(self):
        cmake_layout(self)
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = ["akasha"]
