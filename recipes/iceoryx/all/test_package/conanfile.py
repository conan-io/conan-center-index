import os

from conan import ConanFile
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

    def test(self):
        # ToDo : add an executable which can be
        # executed in container.
        # currently seems shared memory in container is
        # a bad idea (checked on 3 different linux devices
        # always ok - but in container get
        # "fatal SIGBUS signal appeared caused by memset")
        path, dirs, files = next(os.walk(self.cpp.build.bindir))
        print(f"All {len(files)} example files are present")
