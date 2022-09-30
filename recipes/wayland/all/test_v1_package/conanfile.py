import os

from conan import ConanFile
from conan.tools.build import cross_building
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            self.run("wayland-scanner --version", run_environment=True)
            cmd = os.path.join(self.build_folder, "bin", "test_package")
            self.run(cmd, run_environment=True)
