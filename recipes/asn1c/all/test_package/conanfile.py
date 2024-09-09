import os

from conan import ConanFile
from conan.tools.build import can_run, cross_building
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.files import copy


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv", "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        if not cross_building(self):
            copy(self, "MyModule.asn1", src=self.source_folder, dst=self.build_folder)
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")
