from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi", "pkg_config"

    def build_requirements(self):
        self.build_requires("pkgconf/2.0.3")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package_pkgconfig")
            self.run(bin_path, run_environment=True)
            bin_path = os.path.join("bin", "test_package_cmake")
            self.run(bin_path, run_environment=True)
