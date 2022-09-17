from conan import ConanFile
from conan.tools import build
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
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
        if build.can_run(self):
            model_path = os.path.join(self.source_folder, "model.tflite")
            command = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(" ".join([command, model_path]), env="conanrun")
