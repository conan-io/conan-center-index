import os
from conan import ConanFile, tools
from conans import CMake


class SolaceTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.build.cross_building(self, self.settings):
            with tools.files.chdir(self, "bin"):
                self.run(".%sexample" % os.sep, run_environment=True)
