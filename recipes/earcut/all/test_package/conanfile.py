import os

from conans import ConanFile, CMake, tools


class EarcutTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def _configure_cmake(self):
        if not hasattr(self, "_cmake"):
            self._cmake = CMake(self)
            self._cmake.configure()
        
        return self._cmake

    def build(self):
        self._configure_cmake().build()

    def test(self):
        self._configure_cmake().test()
