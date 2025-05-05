from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def requirements(self):
        self.requires("stb/cci.20210910")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            img_path = os.path.join(self.source_folder, os.pardir, "test_package", "test.png")
            self.run(f"{bin_path} {img_path}", run_environment=True)
