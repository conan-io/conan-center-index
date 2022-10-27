from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            font_path = os.path.join(self.source_folder, os.pardir, "test_package", "OpenSans-Bold.ttf")
            self.run(f"{bin_path} {font_path}", run_environment=True)
