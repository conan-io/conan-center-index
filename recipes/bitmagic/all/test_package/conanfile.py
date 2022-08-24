from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        if not self.settings.compiler.get_safe("cppstd"):
            if tools.Version(self.deps_cpp_info["bitmagic"].version) < "7.5.0":
                cmake.definitions["CMAKE_CXX_STANDARD"] = 11
            else:
                cmake.definitions["CMAKE_CXX_STANDARD"] = 17
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
