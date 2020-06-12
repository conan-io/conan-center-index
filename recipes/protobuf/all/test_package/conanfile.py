import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch", "os_build", "arch_build"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if self.settings.os == "Windows" or not tools.cross_building(self.settings):
            bin_path = os.path.abspath(os.path.join("bin", "test_package"))
            self.run(bin_path, run_environment=True)
