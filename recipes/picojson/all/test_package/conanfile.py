from conans import ConanFile, CMake, tools

import os

class PicoJSONTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is
        # in "test_package"
        cmake.configure()
        self._is_multi_configuration = cmake.is_multi_configuration
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            if self._is_multi_configuration:
                os.chdir(str(self.settings.build_type))
            self.run(".%sexample" % os.sep)
