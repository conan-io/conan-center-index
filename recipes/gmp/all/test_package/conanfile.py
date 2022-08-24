from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_CXX"] = self.options["gmp"].enable_cxx
        cmake.definitions["TEST_PIC"] = "fPIC" in self.options["gmp"] and self.options["gmp"].fPIC
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
            if self.options["gmp"].enable_cxx:
                bin_path = os.path.join("bin", "test_package_cpp")
                self.run(bin_path, run_environment=True)
