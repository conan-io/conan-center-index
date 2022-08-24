from conan import ConanFile, tools
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["MSGPACK_C_API"] = self.options["msgpack"].c_api
        cmake.definitions["MSGPACK_CPP_API"] = self.options["msgpack"].cpp_api
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if self.options["msgpack"].c_api:
                bin_c_path = os.path.join("bin", "test_package_c")
                self.run(bin_c_path, run_environment=True)
            if self.options["msgpack"].cpp_api:
                bin_cpp_path = os.path.join("bin", "test_package_cpp")
                self.run(bin_cpp_path, run_environment=True)
