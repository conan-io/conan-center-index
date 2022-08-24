from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "pkg_config"

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            mps = os.path.join(self.source_folder, "sample.mps")
            self.run("{} {}".format(bin_path, mps), run_environment=True)
