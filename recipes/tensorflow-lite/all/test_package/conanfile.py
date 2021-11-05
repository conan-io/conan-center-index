import os
from conans import ConanFile, CMake, tools


class TensorflowLiteTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            model_path = os.path.join("bin", "model.tflite")
            command = os.path.join("bin", "example")
            self.run(" ".join([command, model_path]), run_environment=True)
