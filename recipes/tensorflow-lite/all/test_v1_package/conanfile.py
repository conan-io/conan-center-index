from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            model_path = os.path.join(self.recipe_folder, os.pardir, "test_package", "model.tflite")
            command = os.path.join("bin", "test_package")
            self.run(f"{command} {model_path}", run_environment=True)
