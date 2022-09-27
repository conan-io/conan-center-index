from conans import ConanFile, CMake
from conan.tools.build import cross_building


# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run("yasm --help", run_environment=True)
