from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import copy
from conan.tools.cmake import cmake_layout, CMake
import os


# It will become the standard on Conan 2.x
class TestDrLibsConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_DrLibs")
            copy(self, "sample.wav", self.cpp.build.bindir, self.build_folder)
            self.run(bin_path, env="conanrun")