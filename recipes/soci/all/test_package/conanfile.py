import os
from conans import ConanFile, CMake, tools

class SociTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    # def configure(self):
    #     self.options["soci"].shared     = True
    #     self.options["soci"].empty      = True

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(".%ssoci.tests" % os.sep, run_environment=True)
