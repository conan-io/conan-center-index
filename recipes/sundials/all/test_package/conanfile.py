import os
from conans import ConanFile, CMake, tools


class SundialsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    short_paths = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            self.run(os.path.join("bin", "test_package"),
                     run_environment=True)
