from conans import ConanFile, CMake
from conans.errors import ConanInvalidConfiguration
import os


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        cmd = os.path.join("bin", "hello")
        try:
            self.run(cmd)
            # executable ran successful ==> os must be Macos
            assert self.settings.os == "Macos"
        except ConanException:
            # executable failed ==> os must be some Apple os, but never Macos
            assert tools.is_apple_os(self.settings.os) and self.settings.os != "Macos"
