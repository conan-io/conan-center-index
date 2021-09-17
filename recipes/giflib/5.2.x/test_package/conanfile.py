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
            bin_path = os.path.join("bin", "test_package")
            self.run("{} testimg.gif".format(bin_path), run_environment=True)
            assert os.path.isfile("testimg.gif")
            self.run("gif2rgb -o testimg.rgb testimg.gif".format(bin_path), run_environment=True)
            assert os.path.isfile("testimg.rgb.R")
