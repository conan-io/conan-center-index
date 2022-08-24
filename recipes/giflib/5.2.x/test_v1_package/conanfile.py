# pylint: skip-file
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
            self.run(f"{bin_path} testimg.gif", run_environment=True)
            assert os.path.isfile("testimg.gif")
            if self.options["giflib"].utils:
                self.run("gif2rgb -o testimg.rgb testimg.gif", run_environment=True)
                assert os.path.isfile("testimg.rgb.R")
