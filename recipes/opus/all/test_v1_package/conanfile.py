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
            bin_path = os.path.join("bin", "test_package")
            pcm_path = os.path.join(self.source_folder, os.pardir, "test_package", "test.pcm")
            self.run(f"{bin_path} {pcm_path} out.pcm", run_environment=True)
