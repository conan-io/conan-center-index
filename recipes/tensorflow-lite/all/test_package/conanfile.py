from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            model_path = os.path.join(self.source_folder, "model.tflite")
            command = os.path.join("bin", "test_package")
            self.run(" ".join([command, model_path]), run_environment=True)
