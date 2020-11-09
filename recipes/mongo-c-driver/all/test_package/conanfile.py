import os
from conans import ConanFile, CMake, tools


class MongoCDriverTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["MONGO-C-DRIVER_SHARED"] = self.options["mongo-c-driver"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(os.path.join("bin", "mongo-c-driver-tester"),
                     run_environment=True)
