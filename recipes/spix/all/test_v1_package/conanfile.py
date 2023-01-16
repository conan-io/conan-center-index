from conans import ConanFile, CMake
from conan.tools.build import cross_building
from conan.tools.files import replace_in_file
from conan.tools.scm import Version
import os


class TestSpixV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_spix")
            self.run(bin_path, run_environment=True)
