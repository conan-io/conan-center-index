import os

from conans import ConanFile, CMake, tools


class XsimdTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        if tools.is_apple_os(self.settings.os) and self.settings.arch in ["armv8", "armv8_32", "armv8.3"]:
            cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
