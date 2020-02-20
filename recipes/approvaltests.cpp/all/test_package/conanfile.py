import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"
    default_options = {
        "approvaltests.cpp:with_catch2": True,
        "approvaltests.cpp:with_gtest": True,
        "approvaltests.cpp:with_doctest": True
    }


    def build(self):
        cmake = CMake(self)

        if self.options["approvaltests.cpp"].with_catch2:
            cmake.definitions["WITH_CATCH"] = True
        if self.options["approvaltests.cpp"].with_gtest:
            cmake.definitions["WITH_GTEST"] = True
        if self.options["approvaltests.cpp"].with_doctest:
            cmake.definitions["WITH_DOCTEST"] = True

        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            self.output.warn("Skipping run cross built package")
            return

        bin_path = os.path.join("bin", "test_package")
        if self.options["approvaltests.cpp"].with_catch2:
            self.run(bin_path + "_catch", run_environment=True)
        if self.options["approvaltests.cpp"].with_gtest:
            self.run(bin_path + "_gtest", run_environment=True)
        elif self.options["approvaltests.cpp"].with_doctest:
            self.run(bin_path + "_doctest", run_environment=True)
