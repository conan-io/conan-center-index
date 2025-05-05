from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cache = os.path.join(self.build_folder, "CMakeCache.txt")
        if os.path.exists(cache):
            self.output.info(f"Removing {cache}")
            os.remove(cache)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
