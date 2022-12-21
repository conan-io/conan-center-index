import os

from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.build import can_run


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake_find_package", "cmake_find_package_multi"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not can_run(self):
            return
        for test in ["bigtable", "pubsub", "spanner", "speech", "storage"]:
            cmd = os.path.join(self.cpp.build.bindir, test)
            self.run(cmd, env="conanrun")
