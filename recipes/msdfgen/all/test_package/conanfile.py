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
        if not tools.cross_building(self.settings):
            ttf_path = os.path.join(self.source_folder, "OpenSans-Bold.ttf")
            bin_path = os.path.join("bin", "test_package")
            self.run("{0} {1}".format(bin_path, ttf_path), run_environment=True)
