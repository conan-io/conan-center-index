from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps


class CCLarifyRecipe(ConanFile):
    name = "hyper-cclarify"
    version = "1.0"
    package_type = "library"

    license = "GPLv3"
    author = "HyperWinX"
    url = "https://github.com/HyperWinX/CClarify.git"
    description = "Small and powerful logging library for C applications"
    topics = ("c", "logging")

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "std": [99, 11, 17, 23]}
    default_options = {"shared": False, "fPIC": True, "std": 17}

    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_C_STANDARD"] = str(self.options.std.value)
        tc.variables["CMAKE_C_STANDARD_REQUIRED"] = "ON"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["cclarify"]

