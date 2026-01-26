from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy
import os


class NekoNetworkConan(ConanFile):
    name = "neko-network"
    version = "1.0.1"
    license = "MIT OR Apache-2.0"
    author = "moehoshio"
    url = "https://github.com/moehoshio/NekoNetwork"
    description = "Neko Network is a modern, easy-to-use, and efficient C++20 network library built on top of libcurl."
    topics = ("cpp", "network", "library", "cross-platform", "neko", "http", "websocket", "curl")
    
    settings = "os", "compiler", "build_type", "arch"
    package_type = "static-library"
    exports_sources = "CMakeLists.txt", "include/*", "src/*", "tests/*", "cmake/*", "docs/*", "LICENSE", "README.md"
    
    def requirements(self):
        # self.requires("neko-schema/[*]")
        # self.requires("neko-function/[*]")
        # self.requires("neko-log/[*]")
        # self.requires("neko-system/[*]")
        self.requires("libcurl/[*]")
        
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        # Automatically fetch NekoSchema and NekoFunction until it is available in Conan
        tc.variables["NEKO_NETWORK_AUTO_FETCH_DEPS"] = True
        # Disable building tests for dependencies
        tc.variables["NEKO_NETWORK_BUILD_TESTS"] = False
        tc.variables["NEKO_SCHEMA_BUILD_TESTS"] = False
        tc.variables["NEKO_FUNCTION_BUILD_TESTS"] = False
        tc.variables["NEKO_LOG_BUILD_TESTS"] = False
        tc.variables["NEKO_SYSTEM_BUILD_TESTS"] = False
        # Help CMake find CURL
        tc.variables["CMAKE_FIND_PACKAGE_PREFER_CONFIG"] = True
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.cppm", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        # Set the CMake package file name to match the official CMake config
        self.cpp_info.set_property("cmake_file_name", "NekoNetwork")
        
        # Main target
        self.cpp_info.components["NekoNetwork"].set_property("cmake_target_name", "Neko::Network")
        self.cpp_info.components["NekoNetwork"].includedirs = ["include"]
        # Library target with compiled code
        # Note: Library will be installed via cmake.install() in package()
        lib_folder = os.path.join(self.package_folder, "lib")
        self.cpp_info.components["NekoNetwork"].libs = ["NekoNetwork"]
        # Link libcurl dependency
        self.cpp_info.components["NekoNetwork"].requires = ["libcurl::libcurl"]
    
    def package_id(self):
        self.info.clear()


