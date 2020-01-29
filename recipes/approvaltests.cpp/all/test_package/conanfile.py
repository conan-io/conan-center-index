import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)

        if self.options["approvaltests.cpp"].test_framework == "catch2":
            cmake.definitions["WITH_CATCH"] = True
        elif self.options["approvaltests.cpp"].test_framework == "gtest":
            cmake.definitions["WITH_GTEST"] = True
        elif self.options["approvaltests.cpp"].test_framework == "doctest":
            cmake.definitions["WITH_DOCTEST"] = True

        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            self.output.warn("Skipping run cross built package")
            return

        bin_path = os.path.join("bin", "test_package")
        self.run(bin_path, run_environment=True)
