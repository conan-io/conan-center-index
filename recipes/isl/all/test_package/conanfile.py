from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", 'CMakeDeps'

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join(".", "test_package")
            self.run(bin_path, env='conanrun')
