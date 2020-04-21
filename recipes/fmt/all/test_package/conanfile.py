import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package_multi", "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["FMT_HEADER_ONLY"] = self.options["fmt"].header_only
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin","test_package"), run_environment=True)
            self.run(os.path.join("bin","test_ranges"), run_environment=True)
