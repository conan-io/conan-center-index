from conans import ConanFile, CMake, tools
from io import StringIO
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        bin_path = os.path.join("bin", "test_package")
        buffer = StringIO()
        try:
           self.run(bin_path, run_environment=True, output=buffer)
           self.output.success("enough.c test passed")
        except: # print output of test in case of error
            self.output.error(buffer.getvalue())
