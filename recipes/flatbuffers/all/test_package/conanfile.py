from conan import ConanFile
from conan.tools.build import can_run, cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if not (hasattr(self, "settings_build") and cross_building(self) and self.options["flatbuffers"].header_only):
            self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FLATBUFFERS_HEADER_ONLY"] = self.dependencies["flatbuffers"].options.header_only
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
            sample_binary = os.path.join(self.cpp.build.bindirs[0], "sample_binary")
            self.run(sample_binary, env="conanrun")
