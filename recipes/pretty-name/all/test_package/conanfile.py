from conans import ConanFile, CMake

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        self.cmake = CMake(self)
        self.cmake.configure()
        self.cmake.build()

    def build_requirements(self):
        self.build_requires("cmake/3.18.0")

    def test(self):
        self.cmake.test()
