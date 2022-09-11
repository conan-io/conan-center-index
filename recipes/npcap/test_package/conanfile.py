import os
from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    name = "npcap_test"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
