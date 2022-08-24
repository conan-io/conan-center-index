from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DOUBLE_PRECISION"] = self.options["fftw"].precision == "double"
        cmake.definitions["ENABLE_SINGLE_PRECISION"] = self.options["fftw"].precision == "single"
        cmake.definitions["ENABLE_LONG_DOUBLE_PRECISION"] = self.options["fftw"].precision == "longdouble"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
