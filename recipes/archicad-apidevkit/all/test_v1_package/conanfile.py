from conan import ConanFile
from conan.tools.build import cross_building
from conans import CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def test(self):
        if not cross_building(self):
            devkit_path = os.environ.get("AC_API_DEVKIT_DIR")
            bin_path = os.path.join(
                devkit_path, "Tools", "OSX", "ResConv")
            self.run(bin_path, run_environment=True, ignore_errors=True)
