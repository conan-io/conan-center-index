from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["MONGO-CXX-DRIVER_POLYFILL"] = self.options["mongo-cxx-driver"].polyfill
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
