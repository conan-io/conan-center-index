from os import path
from conan import ConanFile #, tools
from conan.tools.cmake import CMakeToolchain, CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run(path.join(".","test_package"), run_environment=True)
