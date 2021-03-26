from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_DOUBLE_PRECISION"] = self.options["fftw"].precision == "double"
        cmake.definitions["ENABLE_SINGLE_PRECISION"] = self.options["fftw"].precision == "single"
        cmake.definitions["ENABLE_LONG_DOUBLE_PRECISION"] = self.options["fftw"].precision == "longdouble"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
