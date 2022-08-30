from conans import CMake
from conan import ConanFile
from conan.tools.build import cross_building
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"
    options = {"branch_version" : [True, False], "allow_libiconv": [True, False]}
    default_options = {"branch_version": False, "allow_libiconv": True}

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
