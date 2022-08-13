import os

from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "arch", "build_type", "compiler", "os"
    generators = "cmake", "cmake_find_package_multi"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run("{0}".format(bin_path), run_environment=True)
