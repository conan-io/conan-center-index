from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_CHIMERA"] = self.options["hyperscan"].build_chimera
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "hs_example")
            self.run(bin_path, run_environment=True)

            if self.options["hyperscan"].build_chimera:
                bin_path = os.path.join("bin", "ch_example")
                self.run(bin_path, run_environment=True)
