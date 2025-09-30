from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import rmdir
import os

class OptionsPricingModelsConan(ConanFile):
    name = "OptionsPricingModels"
    version = "1.0"
    license = "MIT"
    author = "Dylan Aldridge"
    url = "https://github.com/AldridgeDylan/Option-Pricing-Models"
    description = "Option Pricing Models implemented in C++ using various algorithms."
    topics = ("finance", "option-pricing", "black-scholes")
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "tests/*"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("gtest/1.13.0")

    def generate(self):
        pass

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self.package_folder / "share")
        rmdir(self.package_folder / "lib/cmake")

    def package_info(self):
        self.cpp_info.libs = ["OptionsPricingModels"]
