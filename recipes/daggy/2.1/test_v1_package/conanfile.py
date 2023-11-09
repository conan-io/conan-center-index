import os

from conans import ConanFile, CMake, tools, RunEnvironment


class DaggyTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi", "cmake_paths", "cmake_find_package"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.21 <4]")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
