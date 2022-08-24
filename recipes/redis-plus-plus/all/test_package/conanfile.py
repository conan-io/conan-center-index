import os
from conan import ConanFile, tools
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILDING_SHARED"] = self.options["redis-plus-plus"].shared
        if tools.Version(self.deps_cpp_info["redis-plus-plus"].version) < "1.3.0":
            cmake.definitions["CMAKE_CXX_STANDARD"] = 11
        else:
            cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
