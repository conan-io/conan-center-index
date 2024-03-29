from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DOUBLE_PRECISION"] = self.options["fftw"].precision_double
        cmake.definitions["ENABLE_SINGLE_PRECISION"] = self.options["fftw"].precision_single
        cmake.definitions["ENABLE_LONG_DOUBLE_PRECISION"] = self.options["fftw"].precision_longdouble
        cmake.definitions["ENABLE_QUAD_PRECISION"] = self.options["fftw"].precision_quad
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
