import os
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout

class TestOpenE57Conan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not conan.tools.build.cross_building(self):
            bin_path = os.path.join("bin", "opene57_example")
            self.run(bin_path, run_environment=True)
