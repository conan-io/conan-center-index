from conans import ConanFile, CMake
from conan.tools.build import cross_building
from conan.tools.files import mkdir
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
            input_file = os.path.join(self.source_folder, os.pardir, "test_package", "DCMTK_JPEGExt_12Bits.dcm")
            test_dir = "test_dir"
            mkdir(self, test_dir)
            output_file = os.path.join(test_dir, "output.dcm")
            self.run([bin_path, input_file, output_file], run_environment=True)
