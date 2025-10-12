from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os
import yaml


class UnilinkConan(ConanFile):
    name = "unilink"
    version = "0.1.0"
    description = "Unified async communication library for TCP and Serial communication"
    license = "Apache-2.0"
    url = "https://github.com/jwsung91/unilink"
    homepage = "https://github.com/jwsung91/unilink"
    topics = ("async", "communication", "tcp", "serial", "networking", "c++17")
    
    # Package metadata
    author = "Jinwoo Sung <jwsung91@example.com>"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_examples": [True, False],
        "build_tests": [True, False],
        "build_docs": [True, False],
        "enable_config": [True, False],
        "enable_memory_tracking": [True, False],
        "enable_pkgconfig": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "build_examples": False,
        "build_tests": False,
        "build_docs": False,
        "enable_config": True,
        "enable_memory_tracking": True,
        "enable_pkgconfig": True,
    }
    
    # CMake configuration
    generators = "CMakeToolchain"
    exports_sources = "CMakeLists.txt", "cmake/*", "unilink/*", "examples/*", "test/*", "docs/*", "package/*", "LICENSE", "NOTICE", "README.md"
    
    def export_sources(self):
        copy(self, "conandata.yml", src=self.recipe_folder, dst=self.export_sources_folder)
    
    def _load_conandata(self):
        conandata_path = os.path.join(self.recipe_folder, "conandata.yml")
        if os.path.exists(conandata_path):
            with open(conandata_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def requirements(self):
        # Boost system library - version compatibility based on platform
        if self.settings.os == "Linux":
            # Ubuntu version-specific Boost requirements
            if self.settings.compiler.version and Version(self.settings.compiler.version) < "11.0":
                # Ubuntu 20.04: GCC 9-10, Boost 1.65+
                self.requires("boost/1.65.1")
            elif self.settings.compiler.version and Version(self.settings.compiler.version) < "13.0":
                # Ubuntu 22.04: GCC 11-12, Boost 1.74+
                self.requires("boost/1.74.0")
            else:
                # Ubuntu 24.04+: GCC 13+, try Boost 1.83+ first, fallback to 1.74+
                try:
                    self.requires("boost/1.83.0")
                except:
                    self.requires("boost/1.74.0")
        else:
            # Non-Linux platforms: use latest Boost
            self.requires("boost/1.70.0")
    
    def build_requirements(self):
        if self.options.build_tests:
            self.tool_requires("cmake/[>=3.12]")
        if self.options.build_docs:
            self.tool_requires("doxygen/1.9.8")
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        
        # Run tests if enabled
        if self.options.build_tests:
            cmake.test()
    
    def package(self):
        # Copy license files
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "NOTICE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        # Copy headers
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "unilink"), dst=os.path.join(self.package_folder, "include", "unilink"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "unilink"), dst=os.path.join(self.package_folder, "include", "unilink"))
        
        # Copy libraries
        if self.options.shared:
            copy(self, "*.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dylib*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        
        # Copy CMake files
        copy(self, "unilinkConfig.cmake", src=self.build_folder, dst=os.path.join(self.package_folder, "lib", "cmake", "unilink"))
        copy(self, "unilinkConfigVersion.cmake", src=self.build_folder, dst=os.path.join(self.package_folder, "lib", "cmake", "unilink"))
        copy(self, "unilinkTargets.cmake", src=self.build_folder, dst=os.path.join(self.package_folder, "lib", "cmake", "unilink"))
        copy(self, "unilinkTargets-*.cmake", src=self.build_folder, dst=os.path.join(self.package_folder, "lib", "cmake", "unilink"))
        
        # Copy pkg-config file if enabled
        if self.options.enable_pkgconfig:
            copy(self, "unilink.pc", src=self.build_folder, dst=os.path.join(self.package_folder, "lib", "pkgconfig"))
        
        # Copy documentation if enabled
        if self.options.build_docs:
            copy(self, "*", src=os.path.join(self.source_folder, "docs", "html"), dst=os.path.join(self.package_folder, "share", "doc", "unilink", "html"))
        
        # Copy examples if enabled
        if self.options.build_examples:
            copy(self, "*", src=os.path.join(self.source_folder, "examples"), dst=os.path.join(self.package_folder, "share", "unilink", "examples"))
    
    def package_info(self):
        # Set target name
        self.cpp_info.set_property("cmake_target_name", "unilink::unilink")
        self.cpp_info.set_property("cmake_file_name", "unilink")
        
        # Set include directories
        self.cpp_info.includedirs = ["include"]
        
        # Set library directories
        self.cpp_info.libdirs = ["lib"]
        
        # Set libraries
        if self.options.shared:
            self.cpp_info.libs = ["unilink"]
        else:
            self.cpp_info.libs = ["unilink_static"]
        
        # Set system libraries
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "wsock32"]
        
        # Set compile definitions
        if self.options.enable_config:
            self.cpp_info.defines.append("UNILINK_ENABLE_CONFIG=1")
        if self.options.enable_memory_tracking:
            self.cpp_info.defines.append("UNILINK_ENABLE_MEMORY_TRACKING=1")
        
        # Set C++ standard
        self.cpp_info.cxxflags = ["-std=c++17"]
        
        # Set pkg-config name
        if self.options.enable_pkgconfig:
            self.cpp_info.set_property("pkg_config_name", "unilink")
        
        # Set component information
        self.cpp_info.components["unilink"].set_property("cmake_target_name", "unilink::unilink")
        self.cpp_info.components["unilink"].libs = self.cpp_info.libs
        self.cpp_info.components["unilink"].system_libs = self.cpp_info.system_libs
        self.cpp_info.components["unilink"].defines = self.cpp_info.defines
        self.cpp_info.components["unilink"].cxxflags = self.cpp_info.cxxflags
        
        # Add Boost dependency
        self.cpp_info.components["unilink"].requires = ["boost::boost"]
    
    def package_id(self):
        # Ensure that shared/static builds are different packages
        # The package_id is automatically handled by Conan based on options
        pass
