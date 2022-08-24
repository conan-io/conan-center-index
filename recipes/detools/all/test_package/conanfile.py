import os

from conan import ConanFile, tools
from conan.tools.cmake import CMake


class DetoolsTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    def build_requirements(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # Attempting to use @rpath without CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG being
            # set. This could be because you are using a Mac OS X version less than 10.5
            # or because CMake's platform configuration is corrupt.
            self.build_requires("cmake/3.20.1")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self):
            return

        bin_path = os.path.join("bin", "test_package")
        old_path = os.path.join(self.source_folder, "old")
        patch_path = os.path.join(self.source_folder, "patch")
        patched_path = os.path.join(self.build_folder, "patched")

        self.run(f"{bin_path} {old_path} {patch_path} {patched_path}",
                 run_environment=True)
