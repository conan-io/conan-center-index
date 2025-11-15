from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy
import os


class NekoSchemaConan(ConanFile):
    name = "neko-schema"
    version = "1.0.4"
    license = "MIT OR Apache-2.0"
    author = "moehoshio"
    url = "https://github.com/moehoshio/NekoSchema"
    description = "A lightweight C++20 header-only library providing fundamental type definitions and utilities for the Neko ecosystem"
    topics = ("c++20", "header-only", "schema", "types", "auto-srcLoc" , "utilities")
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "enable_module": [True, False],
    }
    default_options = {
        "enable_module": False,
    }
    
    # Header-only library
    package_type = "header-library"
    no_copy_source = True
    
    exports_sources = "CMakeLists.txt", "include/*", "tests/*", "LICENSE", "README.md"
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NEKO_SCHEMA_BUILD_TESTS"] = False
        tc.variables["NEKO_SCHEMA_ENABLE_MODULE"] = self.options.enable_module
        tc.variables["NEKO_SCHEMA_AUTO_FETCH_DEPS"] = False
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.cppm", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        
        # Set the CMake package file name to match the official CMake config
        self.cpp_info.set_property("cmake_file_name", "NekoSchema")
        
        # Main header-only target
        self.cpp_info.components["NekoSchema"].set_property("cmake_target_name", "Neko::Schema")
        self.cpp_info.components["NekoSchema"].includedirs = ["include"]
        self.cpp_info.components["NekoSchema"].requires = []
        
        # C++20 requirements
        self.cpp_info.components["NekoSchema"].cxxflags = []
        
        # Module support (if enabled)
        if self.options.enable_module:
            self.cpp_info.components["NekoSchemaModule"].set_property("cmake_target_name", "Neko::Schema::Module")
            self.cpp_info.components["NekoSchemaModule"].includedirs = ["include"]
    
    def package_id(self):
        self.info.clear()

