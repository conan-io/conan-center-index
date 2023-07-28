import os

from conans import ConanFile, CMake
from conan.tools.build import cross_building

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            for test in ["", "-mb", "-signal"]:
                self.run("test_package{}".format(test), run_environment=True)
