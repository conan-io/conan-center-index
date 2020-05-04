import os

from conans import ConanFile, CMake, tools


class KcovTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = ["cmake","virtualenv"]

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_BUILD_TYPE"]="Debug"
        cmake.configure()
        cmake.build()
    

    def test(self):
        if not tools.cross_building(self.settings):
            #os.chdir("bin")
            self.run("kcov --exclude-pattern=/usr/ --include-path=${CMAKE_CURRENT_LIST_DIR} cov ./example")
