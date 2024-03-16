from conans import ConanFile, CMake
from conan.tools.build import cross_building
from conan.tools.scm import Version
import os

# legacy validation with Conan 1.x
class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        version = self.tested_reference_str.split('/')[1].split('#')[0]
        cmake.configure(
            defs={"LIBASSERT2": "True"} if Version(version) >= Version("2.0.0") else {}
        )
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
