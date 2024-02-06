from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir

class UpCpp(ConanFile):
    name = "up-cpp"
    package_type = "library"
    license = "Apache-2.0 license"
    url = "https://github.com/MelamudMichael/up-cpp"
    description = "This module contains the data model structures as well as core functionality for building uProtocol"
    topics = ("utransport sdk", "transport")
    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    requires = [
        "spdlog/1.13.0",
        "fmt/10.2.1",
        "gtest/1.14.0"]

    generators = "CMakeDeps"

    def source(self):
        self.run("git clone https://github.com/eclipse-uprotocol/up-core-api.git")
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        
    def requirements(self):
        self.requires("protobuf/3.21.12")
       # self.requires("gtest/1.14.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
      #  tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = True
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
