from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            font = os.path.join(self.source_folder, "..", "test_package", "example.ttf")
            bin_path = os.path.join("bin", "test_package")
            self.run(f"{bin_path} {font}", run_environment=True)

