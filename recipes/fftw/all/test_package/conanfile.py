from conans import ConanFile, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_SINGLE_PRECISION"] = self.options["fftw"].precision == "single"
        cmake.definitions["ENABLE_LONG_DOUBLE_PRECISION"] = self.options["fftw"].precision == "longdouble"
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        self.run(bin_path, run_environment=True)
