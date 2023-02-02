import os
from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.layout import cmake_layout
from conan.tools.build import cross_building


class LibniceTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def layout(self):
        cmake_layout(self)

    def test(self):
        if not cross_building(self, skip_x64_x86=True):
            cmd = os.path.join(self.cpp.build.bindirs[0], "example")
            self.run(cmd, env="conanrun")
