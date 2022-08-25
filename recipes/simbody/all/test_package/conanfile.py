import os

from conans import CMake, ConanFile, tools


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
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
