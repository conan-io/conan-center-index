import os
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)

        if self._boost_test_supported() and self.dependencies["approvaltests.cpp"].options.with_boosttest:
            tc.variables["WITH_BOOSTTEST"] = True
            print('boot')
        if self.dependencies["approvaltests.cpp"].options.with_catch2:
            tc.variables["WITH_CATCH"] = True
            print('catch')
        if self.dependencies["approvaltests.cpp"].options.with_gtest:
            tc.variables["WITH_GTEST"] = True
            print('gtest')
        if self.dependencies["approvaltests.cpp"].options.with_doctest:
            tc.variables["WITH_DOCTEST"] = True
            print('doctest')
        if self._cpputest_supported() and self.dependencies["approvaltests.cpp"].options.with_cpputest:
            tc.variables["WITH_CPPUTEST"] = True
            print('cppu')

        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            self.output.warn("Skipping test run")
            return

        bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
        self.run(bin_path, env="conanrun")
        if self._boost_test_supported() and self.dependencies["approvaltests.cpp"].options.with_boosttest:
            print("Running Boost")
            self.run(bin_path + "_boosttest", env="conanrun")
        if self.dependencies["approvaltests.cpp"].options.with_catch2:
            print("Running Catch2")
            self.run(bin_path + "_catch", env="conanrun")
        if self.dependencies["approvaltests.cpp"].options.with_gtest:
            print("Running GTest")
            self.run(bin_path + "_gtest", env="conanrun")
        if self.dependencies["approvaltests.cpp"].options.with_doctest:
            print("Running DocTest")
            self.run(bin_path + "_doctest", env="conanrun")
        if self._cpputest_supported() and self.dependencies["approvaltests.cpp"].options.with_cpputest:
            print("Running CppUTest")
            self.run(bin_path + "_cpputest", env="conanrun")

    def _boost_test_supported(self):
        return Version(self.dependencies["approvaltests.cpp"].ref.version) >= "8.6.0"

    def _cpputest_supported(self):
        return Version(self.dependencies["approvaltests.cpp"].ref.version) >= "10.4.0"
