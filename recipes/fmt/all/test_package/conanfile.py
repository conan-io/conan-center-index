import os

from conans import ConanFile, tools
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.layout import cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "PkgConfigDeps", "VirtualRunEnv"

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            # FIXME: Very ugly interface to get the current test executable path
            cmd = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(cmd, env=["conanrunenv"])

            cmd = os.path.join(self.cpp.build.bindirs[0], "test_ranges")
            self.run(cmd, env=["conanrunenv"])
