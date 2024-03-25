from conan.tools.microsoft import is_msvc
from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package_cxx")
            self.run(bin_path, run_environment=True)
            if not is_msvc(self):
                # lerc_computeCompressedSize() fails with a stack overflow on MSVC for some reason
                bin_path = os.path.join("bin", "test_package_c")
                self.run(bin_path, run_environment=True)
