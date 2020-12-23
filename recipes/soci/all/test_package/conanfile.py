import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException

class SociTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def configure(self):
        self.options["soci"].static     = True
        self.options["soci"].cxx11      = True
        self.options["soci"].empty      = True

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5.0":
            raise ConanInvalidConfiguration("gcc minimum required version is 5.0")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["SOCI_SHARED"] = self.options["soci"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(".%ssoci.tests" % os.sep)
