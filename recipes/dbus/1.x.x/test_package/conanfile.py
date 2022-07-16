import os

from conan import ConanFile
from conan.tools.build import cross_building
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi", "VirtualBuildEnv", "VirtualRunEnv"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run("dbus-monitor --help", run_environment=True)
            self.run(os.path.join("bin", "test_package"), run_environment=True)
