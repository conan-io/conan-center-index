import os

from conan import ConanFile, conan_version
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.env import VirtualRunEnv


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    @property
    def _skip_shared_macos(self):
        return conan_version.major == 1 and self.options["flatcc"].shared and is_apple_os(self)

    def generate(self):
        VirtualRunEnv(self).generate(scope="build")
        VirtualRunEnv(self).generate(scope="run")


    def build(self):
        if self._skip_shared_macos:
            return
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if self._skip_shared_macos:
            return
        if can_run(self):
            self.run("flatcc --version")
            bin_path = os.path.join(self.cpp.build.bindir, "monster")
            self.run(bin_path, env="conanrun")
