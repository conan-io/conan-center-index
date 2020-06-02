from conans import ConanFile, CMake, tools
import os

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.run("win_flex --version", run_environment=True)
        self.run("win_bison --version", run_environment=True)

        if not tools.cross_building(self.settings):
            cmake = CMake(self)
            cmake.test()
