import os
from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # Attempting to use @rpath without
            # CMAKE_SHARED_LIBRARY_RUNTIME_C_FLAG being set. This could be
            # because you are using a Mac OS X version less than 10.5 or
            # because CMake's platform configuration is corrupt.
            self.build_requires("cmake/3.20.1")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return


        bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
        self.run(bin_path, env="conanrun")
