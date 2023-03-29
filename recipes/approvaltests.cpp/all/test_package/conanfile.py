from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_BOOSTTEST"] = self.dependencies["approvaltests.cpp"].options.get_safe("with_boosttest", False)
        tc.variables["WITH_CATCH"] = self.dependencies["approvaltests.cpp"].options.with_catch2
        tc.variables["WITH_GTEST"] = self.dependencies["approvaltests.cpp"].options.with_gtest
        tc.variables["WITH_DOCTEST"] = self.dependencies["approvaltests.cpp"].options.with_doctest
        tc.variables["WITH_CPPUTEST"] = self.dependencies["approvaltests.cpp"].options.get_safe("with_cpputest", False)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            self.run(f"ctest --output-on-failure -C {self.settings.build_type}", env="conanrun")
