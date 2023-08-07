from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        for key, value in self.dependencies["openscenegraph"].options.items():
            if key.startswith("with_"):
                tc.variables["OSG_HAS_" + key.upper()] = 1 if value else 0
        if is_apple_os(self):
            tc.variables["OSG_HAS_WITH_GIF"] = 0
            tc.variables["OSG_HAS_WITH_JPEG"] = 0
            tc.variables["OSG_HAS_WITH_PNG"] = 0
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
