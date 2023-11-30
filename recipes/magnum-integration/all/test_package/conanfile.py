from conan import ConanFile
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
        tc.variables["WITH_BULLET"] = self.dependencies["magnum-integration"].options.with_bullet
        tc.variables["WITH_DART"] = self.dependencies["magnum-integration"].options.with_dart
        tc.variables["WITH_EIGEN"] = self.dependencies["magnum-integration"].options.with_eigen
        tc.variables["WITH_GLM"] = self.dependencies["magnum-integration"].options.with_glm
        tc.variables["WITH_IMGUI"] = self.dependencies["magnum-integration"].options.with_imgui
        tc.variables["WITH_OVR"] = self.dependencies["magnum-integration"].options.with_ovr
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

        if self.settings.os == "Emscripten":
            bin_path = os.path.join(self.cpp.build.bindir, "test_package.js")
            self.run(f"node {bin_path}", env="conanrun")
