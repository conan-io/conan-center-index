from conan import ConanFile
from conan.tools.files import get, copy
import os

class StbConan(ConanFile):
    name = "stb"
    description = "Single-file public domain libraries for C/C++"
    license = ("MIT", "Public Domain")
    url = "https://github.com/nothings/stb"
    homepage = "https://github.com/nothings/stb"
    topics = ("graphics", "image", "audio", "header-only")
    
    # No settings/options needed for header-only library
    settings = "os", "compiler", "build_type", "arch"
    
    def source(self):
        # Download stb repository
        get(self, "https://github.com/nothings/stb/archive/refs/heads/master.zip", 
            strip_root=True)
    
    def package(self):
        # Copy all header files to package
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
    
    def package_info(self):
        # Header-only library, no linking needed
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_target_name", "stb::stb")
        
    def package_id(self):
        # Header-only library, so same package for all configurations
        self.info.clear()