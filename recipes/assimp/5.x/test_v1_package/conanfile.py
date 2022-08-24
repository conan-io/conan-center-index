# pylint: skip-file
from conan import ConanFile, tools
from conans import CMake
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
            obj_path = os.path.join(self.source_folder, os.pardir, "test_package", "box.obj")

            bin_path = os.path.join("bin", "test_package")
            self.run("{0} {1}".format(bin_path, obj_path), run_environment=True)

            bin_c_path = os.path.join("bin", "test_package_c")
            self.run("{0} {1}".format(bin_c_path, obj_path), run_environment=True)
