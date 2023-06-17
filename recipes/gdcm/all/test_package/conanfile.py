from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import mkdir
import os

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            input_file = os.path.join(self.source_folder, "DCMTK_JPEGExt_12Bits.dcm")
            test_dir = "test_dir"
            mkdir(self, test_dir)
            output_file = os.path.join(test_dir, "output.dcm")
            self.run(f"\"{bin_path}\" \"{input_file}\" \"{output_file}\"", env="conanrun")
