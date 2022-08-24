import os

from conan import ConanFile, tools
from conans import CMake
from conan.tools.build import cross_building


class HyperscanTestConan(ConanFile):
    settings = "os", "build_type", "arch", "compiler"
    generators = "cmake", "cmake_find_package"


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
