from conan import ConanFile, tools
from conans import CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        version = tools.Version(self.deps_cpp_info["openimageio"].version)
        cmake = CMake(self)
        cmake.definitions["CMAKE_CXX_STANDARD"] = 14 if version >= "2.3.0.0" else 11
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
