from os import path
from conan import ConanFile #, tools
from conan.tools.cmake import CMakeToolchain, CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VTK_IGNORE_CMAKE_CXX11_CHECKS"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run(path.join(".","test_package"), run_environment=True)
