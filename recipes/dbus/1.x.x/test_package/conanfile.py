import os
from conans import ConanFile, CMake, tools


class DbusTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_paths", "cmake_find_package", "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            # we know, on headless CI there is no dbus daemon running, so it won't connect
            # we only need to check that we can compile and link an executable
            self.run(os.path.join("bin", "example"), run_environment=True, ignore_errors=True)
