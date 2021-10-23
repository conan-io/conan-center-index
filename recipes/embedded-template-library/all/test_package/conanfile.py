import os

from conans import ConanFile, CMake, tools


class EmbeddedTemplateLibraryTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            os.chdir("bin")
            if tools.detected_os() == "Windows":
                self.run("example")
            else:
                self.run(".%sexample" % os.sep)
