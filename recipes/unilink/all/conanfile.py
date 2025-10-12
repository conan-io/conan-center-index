from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.54.0"


class UnilinkConan(ConanFile):
    name = "unilink"
    version = "0.1.0"
    description = "Unified async communication library for TCP and Serial communication"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jwsung91/unilink"
    topics = ("async", "communication", "tcp", "serial", "networking", "c++17")
    package_type = "library"
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
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
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
    
    def build_requirements(self):
        self.tool_requires("cmake/[>=3.12]")
        if self.options.build_docs:
            self.tool_requires("doxygen/1.9.8")
    
    def layout(self):
        cmake_layout(self, src_folder="src")
    
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
        
        # Set pkg-config name
        if self.options.enable_pkgconfig:
            self.cpp_info.set_property("pkg_config_name", "unilink")
        
        # Set component information
        self.cpp_info.components["unilink"].set_property("cmake_target_name", "unilink::unilink")
        self.cpp_info.components["unilink"].libs = self.cpp_info.libs
        self.cpp_info.components["unilink"].system_libs = self.cpp_info.system_libs
        self.cpp_info.components["unilink"].defines = self.cpp_info.defines
        
        # Add Boost dependency
        self.cpp_info.components["unilink"].requires = ["boost::boost"]
    
    def package_id(self):
        # Ensure that shared/static builds are different packages
        # The package_id is automatically handled by Conan based on options
        pass
