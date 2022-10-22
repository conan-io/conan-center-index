from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            arg_path = bin_path
            if self.settings.os == "Windows":
                arg_path += ".exe"
            self.run(f"{bin_path} {arg_path}", run_environment=True)
