import os
from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self.run(os.path.join("bin", "sample"), run_environment=True)
            self.run(os.path.join("bin", "socket"), run_environment=True)
            self.run(os.path.join("bin", "https"), run_environment=True)
            self.run(os.path.join("bin", "sqlite"), run_environment=True)
