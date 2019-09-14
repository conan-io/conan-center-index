#!/usr/bin/env python

import os

from conans import ConanFile, CMake, tools


class ConanRecipe(ConanFile):
    name = "catch2"
    description = "A modern, C++-native, header-only, framework for unit-tests, TDD and BDD"
    topics = ("conan", "catch2", "header-only", "unit-test", "tdd", "bdd")
    url = "https://github.com/catchorg/Catch2"
    homepage = url
    license = "BSL-1.0"

    settings = "os", "compiler", "build_type", "arch"

    exports = "LICENSE.txt"

    generators = "cmake"

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "Catch2-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    _build_subfolder = "build_subfolder"

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["CATCH_INSTALL_DOCS"] = "OFF"
        cmake.definitions["CATCH_INSTALL_HELPERS"] = "ON"
        cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder
        )
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses")

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()
