import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _binary_name(self):
        name = "test_package"
        if self.settings.os == "Windows":
            name = f"{name}.exe"
        return name

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], self._binary_name)
            self.run(bin_path, env="conanrun")
