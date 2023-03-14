import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.build import cross_building


class FooTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    # VirtualBuildEnv and VirtualRunEnv can be avoided if "tools.env.virtualenv:auto_use" is defined
    # (it will be defined in Conan 2.0)
    generators = "CMakeDeps", "VirtualRunEnv"
    apply_env = False
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DATE_HEADER_ONLY"] = self.dependencies["date"].options.header_only
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if not cross_building(self):
            cmd = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(cmd, env="conanrun")
