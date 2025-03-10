from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def requirements(self):
        # cpp-lazy>=8.0.0 requires fmt library when neither LZ_STANDALONE or LZ_MODULE_EXPORT are not defined
        self.requires("fmt/10.2.1")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
