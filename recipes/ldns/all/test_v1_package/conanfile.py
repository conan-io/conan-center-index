from conans import ConanFile, CMake
from conans.tools import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.build_requires("pkgconf/2.1.0")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            example = os.path.join("test_package", "example")
            self.run(example, run_environment=True)
