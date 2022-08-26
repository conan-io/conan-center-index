
from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(".", "tixi3_conan_test")
            self.run(bin_path, run_environment=True)
