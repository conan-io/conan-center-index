from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, save
from conan.tools.scm import Version
import os


class ComputoConan(ConanFile):
    name = "computo"
    description = "A functional programming language for data transformations"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/HarryPehkonen/Computo"
    topics = ("functional-programming", "data-transformation", "json", "lisp")
    
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nlohmann_json/3.11.3")

    def build_requirements(self):
        # readline is system dependency for REPL - always required
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], 
            destination=self.source_folder, strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", 
             src=self.source_folder, 
             dst=os.path.join(self.package_folder, "licenses"))
        
        # Copy headers
        copy(self, "*.hpp", 
             src=os.path.join(self.source_folder, "include"), 
             dst=os.path.join(self.package_folder, "include"), 
             keep_path=True)
        
        # Copy library
        copy(self, "*.a", 
             src=self.build_folder, 
             dst=os.path.join(self.package_folder, "lib"))
        copy(self, "*.lib", 
             src=self.build_folder, 
             dst=os.path.join(self.package_folder, "lib"))
        copy(self, "*.so", 
             src=self.build_folder, 
             dst=os.path.join(self.package_folder, "lib"))
        copy(self, "*.dylib", 
             src=self.build_folder, 
             dst=os.path.join(self.package_folder, "lib"))
        copy(self, "*.dll", 
             src=self.build_folder, 
             dst=os.path.join(self.package_folder, "bin"))
        
        # Copy both executables (always built in unified build system)
        copy(self, "computo*", 
             src=self.build_folder, 
             dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "computo")
        self.cpp_info.set_property("cmake_target_name", "computo::computo")
        
        self.cpp_info.libs = ["computo"]
        
        # Both executables are always available
        self.cpp_info.bindirs.append("bin")
        if self.settings.os != "Windows":
            self.cpp_info.system_libs.append("readline")

    def package_id(self):
        # No custom package ID handling needed - unified build always produces same output
        pass