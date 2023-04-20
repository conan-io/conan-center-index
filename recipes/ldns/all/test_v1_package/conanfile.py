from conans import ConanFile, CMake
from conans.tools import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            example = os.path.join("test_package", "example")
            self.run(example, run_environment=True)
