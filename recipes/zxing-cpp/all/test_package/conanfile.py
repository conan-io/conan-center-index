from conan import ConanFile, tools
from conans import CMake
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
            try:
                os.unlink("output.png")
            except FileNotFoundError:
                pass
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)

            assert os.path.isfile("output.png")
