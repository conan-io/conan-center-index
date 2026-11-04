from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeDeps, CMakeToolchain, CMake
from conan.tools.env import VirtualRunEnv
from conan.tools.build import can_run

import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        # required for cmake_path support
        self.tool_requires("cmake/[>=3.20 <4]")

    def generate(self):
        deps = CMakeDeps(self)
        deps.check_components_exist = True
        deps.generate()

        tc = CMakeToolchain(self)
        if self.dependencies[self.tested_reference_str].options.shared:
            tc.variables["LLVM_SHARED"] = True
        tc.generate()

        VirtualRunEnv(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindir, "test_package")
            args = os.path.join(os.path.dirname(__file__), "test_function.ll")
            self.run(f"{cmd} {args}", env="conanrun")
