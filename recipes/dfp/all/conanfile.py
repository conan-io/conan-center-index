from conan import ConanFile
from conan.tools.files import copy
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
import os

required_conan_version = ">=2.0.6"


class DfpConan(ConanFile):
    name = "dfp"
    package_type = "library"

    # Optional metadata
    description = "Decimal Floating Point Arithmetic Library"
    homepage = "https://github.com/epam/DFP/"
    url = "https://github.com/epam/DFP.git"
    license = ("Apache-2.0", "Intel")
    topics = ("decimal", "dfp", "ieee-754", "deltix")
    author = "Andrei Davydov (agdavydov81@gmail.com)"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "LICENSE", "intel-eula.txt", "native/CMakeLists.txt", "native/src/*", "native/include/*"

    def configure(self):
        # it's a C library
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        self.folders.source = "native"

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
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder, ".."))
        copy(self, "intel-eula.txt", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder, ".."))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ddfp"]
