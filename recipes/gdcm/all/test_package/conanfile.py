from conan import ConanFile, tools
from conans import CMake
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
            bin_path = os.path.join("bin", "test_package")
            input_file = os.path.join(self.source_folder, "DCMTK_JPEGExt_12Bits.dcm")
            test_dir = "test_dir"
            tools.mkdir(test_dir)
            output_file = os.path.join(test_dir, "output.dcm")
            self.run([bin_path, input_file, output_file], run_environment=True)
