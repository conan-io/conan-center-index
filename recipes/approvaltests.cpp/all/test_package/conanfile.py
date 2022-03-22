import os
from conans import ConanFile, CMake, tools
from conans.tools import Version


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package_multi"
    default_options = {
        "approvaltests.cpp:with_boosttest": True,
        "approvaltests.cpp:with_catch2": True,
        "approvaltests.cpp:with_gtest": True,
        "approvaltests.cpp:with_doctest": True,
        "approvaltests.cpp:with_cpputest": True
    }


    def build(self):
        cmake = CMake(self)

        if self.options["approvaltests.cpp"].with_boosttest and self._boost_test_supported():
            cmake.definitions["WITH_BOOSTTEST"] = True
        if self.options["approvaltests.cpp"].with_catch2:
            cmake.definitions["WITH_CATCH"] = True
        if self.options["approvaltests.cpp"].with_gtest:
            cmake.definitions["WITH_GTEST"] = True
        if self.options["approvaltests.cpp"].with_doctest:
            cmake.definitions["WITH_DOCTEST"] = True
        if self.options["approvaltests.cpp"].with_cpputest and self._cpputest_supported():
            cmake.definitions["WITH_CPPUTEST"] = True

        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            self.output.warn("Skipping run cross built package")
            return

        bin_path = os.path.join("bin", "test_package")
        if self.options["approvaltests.cpp"].with_boosttest and self._boost_test_supported():
            print("Running Boost")
            self.run(bin_path + "_boosttest", run_environment=True)
        if self.options["approvaltests.cpp"].with_catch2:
            print("Running Catch2")
            self.run(bin_path + "_catch", run_environment=True)
        if self.options["approvaltests.cpp"].with_gtest:
            print("Running GTest")
            self.run(bin_path + "_gtest", run_environment=True)
        if self.options["approvaltests.cpp"].with_doctest:
            print("Running DocTest")
            self.run(bin_path + "_doctest", run_environment=True)
        if self.options["approvaltests.cpp"].with_cpputest and self._cpputest_supported():
            print("Running CppUTest")
            self.run(bin_path + "_cpputest", run_environment=True)

    def _boost_test_supported(self):
        return Version(self.deps_cpp_info["approvaltests.cpp"].version) >= "8.6.0"

    def _cpputest_supported(self):
        return Version(self.deps_cpp_info["approvaltests.cpp"].version) >= "10.4.0"
