import os

from conans import ConanFile, CMake, tools, RunEnvironment


class DaggyTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_paths", "cmake_find_package"

    def build_requirements(self):
        self.build_requires("cmake/3.21.3")

    def build(self):
        cmake = CMake(self)
        if self.settings.os == "Windows":
            cmake.definitions["CMAKE_SYSTEM_VERSION"] = "10.1.18362.1"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "testcpp"), run_environment=True)
            self.run(os.path.join("bin", "testc"), run_environment=True)
