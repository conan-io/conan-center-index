from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.cross_building import cross_building

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            cmake = CMake(self)
            cmake.test()
