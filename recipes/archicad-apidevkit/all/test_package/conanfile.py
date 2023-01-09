from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"
    test_type = "explicit"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            devkit_path = os.environ.get("AC_API_DEVKIT_DIR")
            bin_path = os.path.join(
                devkit_path, "Tools", "OSX", "ResConv")
            self.run(bin_path, run_environment=True, ignore_errors=True)
