from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        if tools.Version(self.deps_cpp_info["libaec"].version) >= "1.0.6":
            cmake.definitions["CMAKE_C_STANDARD"] = "11"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
