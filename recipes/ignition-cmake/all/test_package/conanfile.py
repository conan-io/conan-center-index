import os

from conan import ConanFile, tools
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    test_type = "explicit"
    def requirements(self):
         self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["IGN_CMAKE_VER"] = tools.scm.Version(self.deps_cpp_info["ignition-cmake"].version).major
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
