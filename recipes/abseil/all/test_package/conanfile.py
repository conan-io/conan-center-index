from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run("%s -s" % bin_path, run_environment=True)
            bin_global_path = os.path.join("bin", "test_package_global")
            self.run("%s -s" % bin_global_path, run_environment=True)
