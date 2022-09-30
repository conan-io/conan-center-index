import os

from conan import ConanFile
from conan.tools.build import cross_building
from conans import CMake


class LibcapTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"

    def build_requirements(self):
        self.tool_requires("pkgconf/1.7.4")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "example")
            self.run(bin_path, run_environment=True)
