from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["built_with_ade"] = self.options["opencv"].with_ade
        cmake.definitions["built_with_ffmpeg"] = self.options["opencv"].with_ffmpeg
        cmake.definitions["built_contrib_sfm"] = self.options["opencv"].contrib and self.options["opencv"].contrib_sfm
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
