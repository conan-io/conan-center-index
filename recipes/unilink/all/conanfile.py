from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0"


class UnilinkConan(ConanFile):
    name = "unilink"
    description = "Unified async communication library for TCP and Serial communication"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jwsung91/unilink"
    topics = ("async", "communication", "tcp", "serial", "networking", "c++17")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_config": [True, False],
        "enable_memory_tracking": [True, False],
    }
    default_options = {
        "enable_config": True,
        "enable_memory_tracking": True,
    }
    
    # CMake configuration
    generators = "CMakeToolchain"
    
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            from conan.tools.build import check_min_cppstd
            check_min_cppstd(self, 17)
        
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration(f"{self.ref} requires at least GCC 7")
        
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"{self.ref} requires at least Clang 5")
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
    
    def requirements(self):
        # Boost system library - use stable version
        self.requires("boost/1.74.0")
    
    def layout(self):
        cmake_layout(self, src_folder="src")
    
    def package(self):
        # Copy license files
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        # Copy headers
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "unilink"), dst=os.path.join(self.package_folder, "include", "unilink"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "unilink"), dst=os.path.join(self.package_folder, "include", "unilink"))
    
    def package_info(self):
        # Set target name
        self.cpp_info.set_property("cmake_target_name", "unilink::unilink")
        self.cpp_info.set_property("cmake_file_name", "unilink")
        
        # Set include directories
        self.cpp_info.includedirs = ["include"]
        
        # Set compile definitions
        if self.options.enable_config:
            self.cpp_info.defines.append("UNILINK_ENABLE_CONFIG=1")
        if self.options.enable_memory_tracking:
            self.cpp_info.defines.append("UNILINK_ENABLE_MEMORY_TRACKING=1")
        
        # Add Boost dependency
        self.cpp_info.requires = ["boost::boost"]
