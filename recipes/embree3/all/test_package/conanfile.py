import os
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    name = "pkgtest_embree3"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
