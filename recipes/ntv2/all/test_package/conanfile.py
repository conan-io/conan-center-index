from conan import ConanFile
from conan.tools.cmake import CMake
from conans import tools

class Ntv2TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            cmake = CMake(self)
            with tools.run_environment(self):
                cmake.test()
