from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import collect_libs, get, copy
import os

class PmpConan(ConanFile):
    name = "pmp"
    license = "MIT"
    url = "https://github.com/pmp-library/pmp-library"
    description = "PMP library - a library for processing polygon meshes."
    topics = ("geometry", "mesh processing", "3D", "polygon mesh")
    package_type = "library" 

    # Binary configuration
    settings = "os", "arch", "compiler", "build_type"
    options = {
    "shared": [True, False],
    "examples": [True, False],
    "tests": [True, False],
    "docs": [True, False],
    "vis": [True, False],
    "regressions": [True, False]
    }
    default_options = {
    "shared": False,
    "examples": False,
    "tests": False,
    "docs": False,
    "vis": False,
    "regressions": False    
    }
    
    def requirements(self):
        self.requires("eigen/[>=3.4 <4]", transitive_headers=True)
    
    def layout(self):
        cmake_layout(self, src_folder="src")
        
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)  

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["PMP_BUILD_EXAMPLES"] = self.options.examples
        tc.variables["PMP_BUILD_TESTS"] = self.options.tests
        tc.variables["PMP_BUILD_DOCS"] = self.options.docs
        tc.variables["PMP_BUILD_VIS"] = self.options.vis
        tc.variables["PMP_BUILD_REGRESSIONS"] = self.options.regressions
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
        dst=os.path.join(self.package_folder, "licenses"),
        src=self.source_folder)
    
        cmake = CMake(self)
        cmake.install()
        
    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pmp")
        self.cpp_info.set_property("cmake_target_name", "pmp::pmp")
        self.cpp_info.set_property("pkg_config_name", "pmp")
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.bindirs = ["bin"]              
        self.cpp_info.requires = ["eigen::eigen"]