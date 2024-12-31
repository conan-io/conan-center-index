from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps


class lwlogRecipe(ConanFile):
    name = "lwlog"
    version = "latest"
    package_type = "library"

    # Optional metadata
    license = "MIT"
    author = "Christian Panov"
    url = "https://github.com/ChristianPanov/lwlog"
    description = "Very fast synchronous and asynchronous C++17 logging library"
    topics = ("library", "cpp", "asynchronous", "high-performance", "logger", "logging", "metaprogramming", "logging-library", "cpp17", "low-latency", "logger-middleware", "logging-framework", "cpp17-library", "lwlog")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "Config.cmake.in", "lwlog/src/*", "Sandbox/*"

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
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["lwlog_lib"]
        self.cpp_info.set_property("cmake_file_name", "lwlog")
        self.cpp_info.set_property("cmake_target_name", "lwlog::lwlog_lib")
        self.cpp_info.includedirs = ["include/src"]