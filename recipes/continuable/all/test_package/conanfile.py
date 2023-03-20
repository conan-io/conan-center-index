import os
import platform

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        bin_name = "test_package"
        if platform.system() == "Windows":
            bin_name = "%s.exe" % bin_name
        self.run(os.path.abspath(bin_name))
