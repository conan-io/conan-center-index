import os

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import cross_building


class ConanRmluiTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, run_environment=True)
