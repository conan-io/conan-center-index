from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["TINYSPLINE_CXX"] = self.options["tinyspline"].cxx
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_c_path = os.path.join("bin", "test_package_c")
            self.run(bin_c_path, run_environment=True)
            if self.options["tinyspline"].cxx:
                bin_cpp_path = os.path.join("bin", "test_package_cpp")
                self.run(bin_cpp_path, run_environment=True)
