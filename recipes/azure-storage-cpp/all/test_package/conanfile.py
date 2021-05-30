import os

from conans import ConanFile, CMake, tools


class AwsSdkCppTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        if not self.settings.compiler.cppstd:
            cmake.definitions["CMAKE_CXX_STANDARD"] = 11
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
