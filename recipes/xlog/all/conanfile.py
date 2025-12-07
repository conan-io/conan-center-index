from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.files import copy, save
import os


class XlogConan(ConanFile):
    name = "xlog"
    version = "1.0.0"
    license = "MIT"
    author = "hent83722"
    url = "https://github.com/hent83722/xlog"
    homepage = "https://github.com/hent83722/xlog"
    description = "Lightweight C++17 logging library with multiple sinks (console, file, rotating, syslog, UDP network)"
    topics = ("logging", "c++17", "cross-platform", "header-only", "sinks")
    
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_syslog": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_syslog": True,
    }
    
    exports_sources = "CMakeLists.txt", "include/*", "src/*", "cmake/*", "LICENSE"
    
    def config_options(self):
        if self.settings.os == "Windows":
            self.options.enable_syslog = False
            del self.options.fPIC
    
    def configure(self):
        if self.settings.os == "Windows":
            self.options.enable_syslog = False
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["ENABLE_SYSLOG"] = self.options.enable_syslog
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
        

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)
    
    def package_info(self):
        self.cpp_info.libs = ["xlog"]
        
        self.cpp_info.set_property("cmake_find_mode", "config")
        self.cpp_info.set_property("cmake_file_name", "xlog")
        self.cpp_info.set_property("cmake_target_name", "xlog::xlog")
        

        self.cpp_info.includedirs = ["include"]
        
  
        if self.settings.os in ("Linux", "Macos", "FreeBSD"):
            self.cpp_info.system_libs = ["syslog"]
