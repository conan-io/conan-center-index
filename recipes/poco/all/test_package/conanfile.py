import os
from conans import ConanFile
from conans import CMake


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run(os.path.join("bin", "sample"), run_environment=True)
        self.run(os.path.join("bin", "socket"), run_environment=True)
        self.run(os.path.join("bin", "https"), run_environment=True)
        self.run(os.path.join("bin", "sqlite"), run_environment=True)
