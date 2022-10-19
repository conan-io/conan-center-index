from conans import ConanFile, CMake
from conan.tools.build import cross_building
from conan.tools.microsoft import is_msvc
import os


class TestPackageV1Conan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        # fix "error C2039: '​CheckForDuplicateEntries': is not a member of 'Microsoft::WRL::Details'"
        if is_msvc(self):
            cmake.definitions["CMAKE_SYSTEM_VERSION"] = "10.0.18362.0"
        cmake.configure()
        cmake.build()

    def test(self):
        if not cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
