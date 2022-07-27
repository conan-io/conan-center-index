import os

from conans import ConanFile, CMake, tools


class SystemcComponentsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def requirements(self):
        self.requires("systemc/2.3.3")
        self.requires("systemc-cci/1.0.0")
        self.requires("zlib/1.2.11")
        self.requires("fmt/8.0.1")
        self.requires("boost/1.75.0")
        
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
