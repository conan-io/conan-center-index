from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            test_package_c = os.path.join("bin", "test_package")
            test_package_cpp = os.path.join("bin", "test_package_cpp")
            self.run(test_package_c, run_environment=True)
            self.run(test_package_cpp, run_environment=True)
