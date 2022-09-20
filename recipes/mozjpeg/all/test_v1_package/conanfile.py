from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            img_name = os.path.join(self.source_folder, "testimg.jpg")
            self.run(f"{bin_path} {img_name}", run_environment=True)
