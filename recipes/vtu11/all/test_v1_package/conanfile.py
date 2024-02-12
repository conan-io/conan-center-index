from conans import ConanFile, CMake
from conan.errors import ConanException
from conan.tools.build import cross_building

import os

from pathlib import Path


class TestPackageV1Conan(ConanFile):
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
            test_vtu = Path(self.build_folder, "test.vtu")
            if not test_vtu.exists() or "VTKFile" not in test_vtu.read_text():
                raise ConanException("Failed to generate a viable vtu file")
