import os

from conan.tools.microsoft import is_msvc
from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    test_type = "explicit"
    def requirements(self):
         self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["IGN_CMAKE_VER"] = tools.Version(self.deps_cpp_info["ignition-cmake"].version).major
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if is_msvc(self):
                bin_path = os.path.join(self.cpp.build.bindir, "bin", "test_package")
            else:
                bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
