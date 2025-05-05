from conans import ConanFile, CMake
from conan.tools.build import cross_building
import os


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            # from https://en.wikipedia.org/wiki/Magnet_URI_scheme
            magnet_url = "magnet:?xt=urn:btih:c12fe1c06bba254a9dc9f519b335aa7c1367a88a"
            self.run("{} {}".format(bin_path, magnet_url), run_environment=True)
