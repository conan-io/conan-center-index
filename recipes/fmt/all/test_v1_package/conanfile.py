# pylint: skip-file
from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["FMT_HEADER_ONLY"] = self.options["fmt"].header_only
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
            self.run(os.path.join("bin", "test_ranges"), run_environment=True)
