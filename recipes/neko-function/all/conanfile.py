from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy
import os


class NekoFunctionConan(ConanFile):
    name = "neko-function"
    version = "1.0.7"
    license = "MIT OR Apache-2.0"
    author = "moehoshio"
    url = "https://github.com/moehoshio/NekoFunction"
    description = "A comprehensive modern C++ utility library that provides practical functions for common programming tasks."
    topics = ("cpp", "utility", "modern-cpp", "functions", "neko", "archive", "string", "hash", "sha256" , "uuid" ,"datetime", "iso8601", "module")
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "enable_module": [True, False],
        "enable_archive": [True, False],
        "enable_hash": [True, False],

    }
    default_options = {
        "enable_module": False,
        "enable_archive": False,
        "enable_hash": False,
    }
    
    no_copy_source = True
    
    def set_version(self):
        # Set package type based on options
        if self.options.enable_hash or self.options.enable_archive:
            self.package_type = "library"
        else:
            self.package_type = "header-library"
    
    exports_sources = "CMakeLists.txt", "include/*", "src/*", "tests/*", "cmake/*", "LICENSE", "README.md"

    def requirements(self):
        if self.options.enable_hash:
            self.requires("openssl/[>=3.0]")
        if self.options.enable_archive:
            self.requires("minizip-ng/[>=4.0]")
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NEKO_FUNCTION_BUILD_TESTS"] = False
        tc.variables["NEKO_FUNCTION_ENABLE_MODULE"] = self.options.enable_module
        tc.variables["NEKO_FUNCTION_ENABLE_HASH"] = self.options.enable_hash
        tc.variables["NEKO_FUNCTION_ENABLE_ARCHIVE"] = self.options.enable_archive
        # Automatically fetch NekoSchema until it is available in Conan
        tc.variables["NEKO_FUNCTION_AUTO_FETCH_DEPS"] = True
        tc.variables["NEKO_SCHEMA_BUILD_TESTS"] = False
        tc.generate()
        
        deps = CMakeDeps(self)
        # Set the target name mapping for minizip-ng
        if self.options.enable_archive:
            deps.set_property("minizip-ng", "cmake_find_mode", "both")
            deps.set_property("minizip-ng", "cmake_file_name", "minizip-ng")
        deps.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        if self.options.enable_hash or self.options.enable_archive:
            cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.cppm", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        # Set the CMake package file name to match the official CMake config
        self.cpp_info.set_property("cmake_file_name", "NekoFunction")
        
        # Main target
        self.cpp_info.components["NekoFunction"].set_property("cmake_target_name", "Neko::Function")
        self.cpp_info.components["NekoFunction"].includedirs = ["include"]
        
        # Configure based on package type
        if self.options.enable_hash or self.options.enable_archive:
            # Library target with compiled code
            # Note: Library will be installed via cmake.install() in package()
            import os
            lib_folder = os.path.join(self.package_folder, "lib")
            if os.path.exists(lib_folder):
                self.cpp_info.components["NekoFunction"].libs = ["NekoFunction"]
            
            # Add dependencies
            if self.options.enable_hash:
                self.cpp_info.components["NekoFunction"].requires.append("openssl::openssl")
                self.cpp_info.components["NekoFunction"].defines.append("NEKO_FUNCTION_ENABLE_HASH")
                self.cpp_info.components["NekoFunction"].defines.append("NEKO_IMPORT_OPENSSL")
            
            if self.options.enable_archive:
                self.cpp_info.components["NekoFunction"].requires.append("minizip-ng::minizip-ng")
                self.cpp_info.components["NekoFunction"].defines.append("NEKO_FUNCTION_ENABLE_ARCHIVE")
        else:
            # Header-only target - no libraries
            self.cpp_info.bindirs = []
            self.cpp_info.libdirs = []
        
        # Module support (if enabled)
        if self.options.enable_module:
            self.cpp_info.components["NekoFunctionModule"].set_property("cmake_target_name", "Neko::Function::Module")
            self.cpp_info.components["NekoFunctionModule"].includedirs = ["include"]
            self.cpp_info.components["NekoFunctionModule"].requires = ["NekoFunction"]
    
    def package_id(self):
        self.info.clear()







