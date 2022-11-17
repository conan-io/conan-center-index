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
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            md_path = os.path.join(self.source_folder, "test.md")
            self.run("{} \"{}\"".format(bin_path, md_path), run_environment=True)
