import os

from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["TINYSPLINE_CXX"] = self.options["tinyspline"].cxx
        cmake.definitions["TINYSPLINE_API_0_3"] = tools.Version(self.deps_cpp_info["tinyspline"].version) >= "0.3.0"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_c_path = os.path.join("bin", "test_package_c")
            self.run(bin_c_path, run_environment=True)
            if self.options["tinyspline"].cxx:
                bin_cpp_path = os.path.join("bin", "test_package_cpp")
                self.run(bin_cpp_path, run_environment=True)
