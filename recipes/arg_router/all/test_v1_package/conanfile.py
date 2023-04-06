import os

from conans import ConanFile, CMake
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            cmd = os.path.join(self.cpp.build.bindir,
                               "conan_test_project") + " --help"
            self.run(cmd, env="conanrun")
