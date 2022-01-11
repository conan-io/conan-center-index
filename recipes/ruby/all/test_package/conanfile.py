from conan import ConanFile
from conan.tools.cmake import CMake
from conans import tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("ruby --version", run_environment=True)
            CMake(self).test(output_on_failure=True)
