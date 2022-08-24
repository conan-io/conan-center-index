import os
from conan import ConanFile, tools
from conans import CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            # core component
            bin_path = os.path.join("bin", "test_package_core")
            self.run(bin_path, run_environment=True)
            # lsr component
            if self.options["soxr"].with_lsr_bindings:
                bin_path = os.path.join("bin", "test_package_lsr")
                self.run(bin_path, run_environment=True)
