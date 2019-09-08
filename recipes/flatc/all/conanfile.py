#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Conan recipe package for Google FlatBuffers - Flatc
"""
import os
from conans import ConanFile, CMake, tools


class FlatcConan(ConanFile):
    name = "flatc"
    license = "Apache-2.0"
    url = "https://github.com/uilianries/conan-center-index"
    homepage = "http://google.github.io/flatbuffers/"
    author = "Conan Community"
    topics = ("conan", "flatbuffers", "serialization", "rpc", "json-parser", "installer")
    description = "Memory Efficient Serialization Library"
    settings = "os_build", "arch_build"
    exports_sources = "CMakeLists.txt"
    exports = "../../../LICENSE"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "flatbuffers-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = False
        cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = True
        cmake.definitions["FLATBUFFERS_BUILD_FLATC"] = True
        cmake.definitions["FLATBUFFERS_BUILD_FLATHASH"] = True
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        extension = ".exe" if self.settings.os_build == "Windows" else ""
        self.copy(pattern="flatc" + extension, dst="bin", src="bin")
        self.copy(pattern="flathash" + extension, dst="bin", src="bin")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.PATH.append(bin_path)
