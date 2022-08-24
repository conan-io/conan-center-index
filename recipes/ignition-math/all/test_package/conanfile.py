from conan import ConanFile, tools
from conans import CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["IGN_MATH_MAJOR_VER"] = tools.Version(self.deps_cpp_info["ignition-math"].version).major
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
