from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            zipFile_path = os.path.join(self.source_folder, "zipFile.zip")
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path + " " + zipFile_path, run_environment=True)
