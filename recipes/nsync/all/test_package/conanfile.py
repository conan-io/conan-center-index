import os

from conan import ConanFile, tools
from conans import CMake


class NsyncTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            test_package_c = os.path.join("bin", "test_package")
            test_package_cpp = os.path.join("bin", "test_package_cpp")
            self.run(test_package_c, run_environment=True)
            self.run(test_package_cpp, run_environment=True)
