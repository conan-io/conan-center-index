from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get


class stkRecipe(ConanFile):
    name = "stk"
    version = "5.0.1"
    package_type = "library"

    # Optional metadata
    license = "MIT"
    url = "https://ccrma.stanford.edu/software/stk/"
    description = "The Synthesis ToolKit in C++"
    topics = ("audio", "synthesis")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    #exports_sources = "CMakeLists.txt", "src/*", "include/*"
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
    
    def config_options(self):
        pass

    def configure(self):
        pass

    def layout(self):
        cmake_layout(self, src_folder="src")
    
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
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["stk"]

