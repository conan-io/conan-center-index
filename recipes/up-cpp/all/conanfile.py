from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

class UpCpp(ConanFile):
    name = "up-cpp"
    package_type = "library"
    license = "Apache-2.0 license"
    url = "https://github.com/MelamudMichael/up-cpp"
    description = "This module contains the data model structures as well as core functionality for building uProtocol"
    topics = ("utransport sdk", "transport")
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [False, False]}
    default_options = {"shared": True, "fPIC": False}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "conaninfo/*", "include/*" ,"src/*" , "test/*"
    requires = [
        "spdlog/1.13.0",
        "fmt/10.2.1",
        "gtest/1.14.0"]

    generators = "CMakeDeps"

    def source(self):
        self.run("git clone https://github.com/eclipse-uprotocol/up-core-api.git")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("protobuf/3.21.12")
        self.requires("gtest/1.14.0")

    def layout(self):
        cmake_layout(self)

    def generate(self):
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
        self.cpp_info.libs = ["up-cpp"]
