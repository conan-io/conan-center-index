from conans import ConanFile, CMake, tools
import os

class GDCMTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            input_file = os.path.join(self.source_folder, "DCMTK_JPEGExt_12Bits.dcm")
            test_dir = "test_dir"
            tools.mkdir(test_dir)
            output_file = os.path.join(test_dir, "output.dcm")
            self.run([bin_path, input_file, output_file], run_environment=True)
