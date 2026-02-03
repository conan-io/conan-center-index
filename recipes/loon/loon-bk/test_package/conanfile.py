from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake
from conan.tools.build import can_run
import os

class LoonTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            exe_name = "test_package.exe" if self.settings.os == "Windows" else "test_package"
            exe = os.path.join(self.cpp.build.bindirs[0], exe_name)
            self.run(exe, env="conanrun")