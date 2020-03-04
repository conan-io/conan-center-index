from conans import ConanFile, CMake, tools

import os

class JsonCppTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"

    @property
    def _is_multi_configuration(self):
        cmake = CMake(self)
        return cmake.is_multi_configuration

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = "example"
            if self._is_multi_configuration:
                bin_path = os.path.join(str(self.settings.build_type), bin_path)
            self.run(bin_path, run_environment=True)
