import os

from conans import ConanFile, CMake, tools

class TestPackageHazelcastCxx(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"
    requires = "hazelcastcxx/4.0.0"

    def configure(self):
        if self.settings.compiler == "gcc" or (self.settings.compiler == "clang" and self.settings.os == "Linux"):
            self.settings.compiler.libcxx="libstdc++11"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def build(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"), run_environment=True)
