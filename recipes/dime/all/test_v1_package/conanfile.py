import os
from conans import ConanFile, CMake, tools

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            dxf_path = os.path.join(self.source_folder, os.pardir, "test_package", "testFile_Bug01.dxf")
            self.run(f"{bin_path} {dxf_path}", run_environment=True)
