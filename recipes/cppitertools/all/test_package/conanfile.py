import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ZIP_LONGEST"] = self.dependencies["cppitertools"].options.zip_longest
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if can_run(self):
            cmd = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(cmd, env="conanrun")
            # sense if it was built because we don't have access to:
            # self.dependencies["cppitertools"].options.zip_longest
            cmd = os.path.join(self.cpp.build.bindir, "test_zip_longest")
            if os.path.exists(cmd):
                self.run(cmd, env="conanrun")
