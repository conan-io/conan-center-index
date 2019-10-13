# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def configure(self):    
        if not self.settings.compiler.cppstd:
            self.settings.compiler.cppstd = 17
        elif self.settings.compiler.cppstd.value < "17":
            raise ConanInvalidConfiguration("cpp-taskflow requires c++17")
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
