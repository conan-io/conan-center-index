from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    test_type = "explicit"
    def requirements(self):
         self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        #cmake.definitions["SIMBODY_VER"] = tools.Version(self.deps_cpp_info["simbody"].version).major
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self.settings):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
