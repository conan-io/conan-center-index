import os
from conans import ConanFile, CMake, tools


class DbusTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package", "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("dbus-monitor --help", run_environment=True)
            self.run(os.path.join("bin", "example"), run_environment=True)
