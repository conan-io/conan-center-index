import os

from conans import ConanFile, CMake, tools


class TwitchNativeIpcTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            #bin_path = os.path.join("bin", "example")
            cmd = "{} && {}".format(os.path.join("bin", "example"), os.path.join("bin", "example2"))
            self.run(cmd, run_environment=True)
