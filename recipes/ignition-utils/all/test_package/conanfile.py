from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def requirements(self):
        self.requires("ignition-cmake/2.10.0")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["IGN_UTILS_MAJOR_VER"] = tools.Version(self.deps_cpp_info["ignition-utils"].version).major
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
