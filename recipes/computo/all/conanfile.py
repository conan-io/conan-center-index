from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, get, copy, mkdir, export_conandata_patches, replace_in_file
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
        self.requires("readline/[>8 <9]")
        self.test_requires("gtest/[>1 <2]")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], 
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "-Werror", "")

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
        
        # Copy libraries          
        mkdir(self, os.path.join(self.package_folder, "lib"))

        lib_extensions = [".a", ".lib", ".so", ".dylib"]
        for ext in lib_extensions:
            self.output.warning("Looking for library files with extension: " + ext)
            copy(self, f"*{ext}", 
                 src=self.build_folder, 
                 dst=os.path.join(self.package_folder, "lib"))

        copy(self, "*.dll", 
             src=self.build_folder, 
             dst=os.path.join(self.package_folder, "bin"))
        
        # Copy both executables (always built in unified build system)
        executables = ["computo", "computo_repl"]
        if self.settings.os == "Windows":
            executables = [f"{exe}.exe" for exe in executables]
        
        for exe in executables:
            copy(self, exe, 
                 src=self.build_folder, 
                 dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "computo")
        self.cpp_info.set_property("cmake_target_name", "computo::computo")
        
        self.cpp_info.libs = ["computo"]
