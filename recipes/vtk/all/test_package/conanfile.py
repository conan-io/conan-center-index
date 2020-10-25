import os
from conans import ConanFile, CMake, tools, RunEnvironment

class TestVTKConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake" # Replace "cmake" by "cmake_find_package_multi" to test multi

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            # Replace "bin" by "Debug" on Win or by "." (dot) on Mac when testing "cmake_find_package_multi"
            bin_path = os.path.join("bin", "test_vtk_package")
            self.run(bin_path, run_environment=True)
