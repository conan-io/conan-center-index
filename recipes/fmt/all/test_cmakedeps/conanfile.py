import os
from conans import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan import tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FMT_HEADER_ONLY"] = self.options["fmt"].header_only
        tc.generate()

    def build(self):
        cwd = os.path.dirname(__file__)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(cwd, "..", "test_package"))
        cmake.build()

    def test(self):
        if not tools.cross_building.cross_building(self):
            self.run("test_package", run_environment=True)
            self.run("test_ranges", run_environment=True)
