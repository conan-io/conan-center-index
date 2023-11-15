from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
import os

required_conan_version = ">=1.54.0"


class DfpConan(ConanFile):
    name = "dfp"
    package_type = "library"

    # Optional metadata
    description = "Decimal Floating Point Arithmetic Library"
    homepage = "https://github.com/epam/DFP/"
    url = "https://github.com/conan-io/conan-center-index"
    license = ("Apache-2.0", "Intel")
    topics = ("decimal", "dfp", "ieee-754", "deltix")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        # it's a C library
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.22.0 <4]")

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
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "intel-eula.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ddfp"]
