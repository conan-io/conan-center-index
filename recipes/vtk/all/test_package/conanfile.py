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
        bin_path = os.path.join("bin", "test_vtk_package")  # Replace "bin" by "Debug" for "cmake_find_package_multi"
        if self.settings.os == "Windows":
            self.run(bin_path, run_environment=True)
        elif self.settings.os == "Macos":
            self.run("DYLD_LIBRARY_PATH=%s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path), run_environment=True)
        else:
            self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path), run_environment=True)
