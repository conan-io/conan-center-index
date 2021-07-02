import os
from conans import ConanFile, CMake


class test_pkg_conan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"

    def build(self):
        self.run("make")

    def test(self):
        self.run("./test_package", run_environment=True)
