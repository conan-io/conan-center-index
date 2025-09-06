from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, cmake_layout, CMake
from conan.tools.files import get, copy, save
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os


class AlgebraicHashingConan(ConanFile):
    name = "algebraic-hashing"
    description = "Modern C++20 library for algebraic hash function composition"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/queelius/algebraic_hashing"
    topics = ("hash-functions", "cryptography", "algorithms", "cpp20", "header-only", "mathematics")
    
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    
    # No options for Conan Center - keep it simple
    no_copy_source = True
    
    @property
    def _min_cppstd(self):
        return "20"
    
    @property  
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "clang": "12", 
            "apple-clang": "13",
            "Visual Studio": "16",
            "msvc": "192"
        }
    
    def layout(self):
        cmake_layout(self, src_folder="src")
        
    def requirements(self):
        # Header-only library with no dependencies
        pass
        
    def package_id(self):
        self.info.clear()
        
    def validate(self):
        # Validate C++20 support
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
    
    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ALGEBRAIC_HASHING_BUILD_TESTS"] = False
        tc.variables["ALGEBRAIC_HASHING_BUILD_EXAMPLES"] = False  
        tc.variables["ALGEBRAIC_HASHING_BUILD_BENCHMARKS"] = False
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()
        
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        
    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        
    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        
        self.cpp_info.set_property("cmake_file_name", "AlgebraicHashing")
        self.cpp_info.set_property("cmake_target_name", "AlgebraicHashing::algebraic_hashing")
        
        # Threading support
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        
        # Preprocessor definitions
        self.cpp_info.defines.append("ALGEBRAIC_HASHING_ENABLE_CONCEPTS_CHECKING")
        self.cpp_info.defines.append("ALGEBRAIC_HASHING_ENABLE_STATISTICS")