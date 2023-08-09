import os
from conans import ConanFile, CMake, tools

class TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "pkg_config"

    def build_requirements(self):
        self.build_requires("pkgconf/1.9.3")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
