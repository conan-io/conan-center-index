import os
from conans import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.cross_building import cross_building as tools_cross_building


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FMT_HEADER_ONLY"] = self.dependencies["fmt"].options.header_only
        tc.variables["CMAKE_RUNTIME_OUTPUT_DIRECTORY"] = "bin"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join("..", "test_package"))
        cmake.build()

    def test(self):
        if not tools_cross_building(self):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
            self.run(os.path.join("bin", "test_ranges"), run_environment=True)
