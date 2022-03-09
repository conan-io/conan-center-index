from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        self.build_requires("ignition-cmake/2.5.0")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["IGN_MSGS_MAJOR_VER"] = tools.Version(self.deps_cpp_info["ignition-msgs"].version).major
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
