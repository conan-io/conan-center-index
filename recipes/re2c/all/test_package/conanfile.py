from conans import ConanFile, CMake, tools
import os

# FIXME: uncomment the line below once conan 1.36.0 becomes available on c3i
# required_conan_version = ">=1.36.0"


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    test_type = "build_requires"

    def build(self):
        if not tools.cross_building(self.settings):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
