import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    requires = [
        "catch2/2.11.0",
        "gtest/1.10.0",
        "doctest/2.3.5"
    ]

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            self.output.warn("Skipping run cross built package")
            return

        bin_path = os.path.join("bin", "test_package")
        self.run(bin_path + "_catch", run_environment=True)
        self.run(bin_path + "_gtest", run_environment=True)
        self.run(bin_path + "_doctest", run_environment=True)
