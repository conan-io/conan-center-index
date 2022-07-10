import os
from conans import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.cross_building import cross_building as tools_cross_building
from conan.tools.layout import cmake_layout

required_conan_version = ">=1.43.0"

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FMT_HEADER_ONLY"] = self.dependencies["fmt"].options.header_only
        tc.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools_cross_building(self):
            self.run(os.path.join(self.cpp.build.bindirs[0], "test_package"), run_environment=True)
            self.run(os.path.join(self.cpp.build.bindirs[0], "test_ranges"), run_environment=True)
