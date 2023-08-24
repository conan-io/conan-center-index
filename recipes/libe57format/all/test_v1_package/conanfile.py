from conans import ConanFile, CMake, tools
from conans.tools import Version
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        tested_version = self.tested_reference_str.split('/')[1].split('@')[0].split('#')[0]
        if Version(tested_version) >= Version("3.0.0"):
            print(f'Skipping tests in version {tested_version}')
            return

        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
