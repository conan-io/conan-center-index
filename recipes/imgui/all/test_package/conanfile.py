from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os
import re


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        with_docking = self.dependencies[self.tested_reference_str].conf_info.get("user.imgui:with_docking", False)
        with_test_engine = self.dependencies[self.tested_reference_str].options.get_safe("enable_test_engine", False)
        tc = CMakeToolchain(self)
        tc.variables["DOCKING"] = with_docking
        tc.variables["ENABLE_TEST_ENGINE"] = with_test_engine
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
