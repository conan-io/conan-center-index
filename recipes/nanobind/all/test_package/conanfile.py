import importlib
import sys

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _test_nanobind_module(self):
        sys.path.append(self.build_folder)
        # Cannot use 'import test_package' due to pylint
        test_package = importlib.import_module("test_package")
        assert test_package.add(2, 3) == 5
        self.output.info("test_package.add(2, 3) ran successfully")
        sys.path.pop()

    def test(self):
        if can_run(self):
            self._test_nanobind_module()
