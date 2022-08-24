import os

from conan import ConanFile, tools
from conan.tools.cmake import CMake


class TwitchNativeIpcTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "example"), run_environment=True)
            self.run(os.path.join("bin", "example2"), run_environment=True)
