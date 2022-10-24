from conan import ConanFile
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def test(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
