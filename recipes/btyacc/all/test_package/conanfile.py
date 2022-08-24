import functools
import os

from conan import ConanFile, tools
from conan.tools.cmake import CMake


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        if not tools.cross_building(self):
            self._configure_cmake().build()

    def test(self):
        if not tools.cross_building(self):
            self._configure_cmake().test()
