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
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "3.8":
            raise ConanInvalidConfiguration("clang minimum required version is 3.8")
        if self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) < "10.0":
            raise ConanInvalidConfiguration("apple-clang minimum required version is 10.0")
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "19":
            raise ConanInvalidConfiguration("Visual Studio minimum required version is 19")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["SOCI_SHARED"] = self.options["soci"].shared
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run(".%ssoci.tests" % os.sep)
