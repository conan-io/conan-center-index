from conans import ConanFile, tools
import os

from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("qt/[>=6.0.0]")

    def configure(self):
        self.options["qt"].shared = True
        self.options["qt"].qtdeclarative = True
        self.options["qt"].qtshadertools = True
        self.options["qt"].with_libjpeg = "libjpeg-turbo"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def test(self):
        pass