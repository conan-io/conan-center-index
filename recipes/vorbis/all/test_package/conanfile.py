from conans import ConanFile, CMake, tools
import os
import subprocess
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        with tools.chdir("bin"):
            self.run("test_package < %s > sample.ogg" % os.path.join(self.source_folder, '8kadpcm.wav'), run_environment=True)
