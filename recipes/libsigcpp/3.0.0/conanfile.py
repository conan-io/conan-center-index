#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools

class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    version = "3.0.0"
    url = "https://github.com/libsigcplusplus/libsigcplusplus"
    homepage = "https://libsigcplusplus.github.io/libsigcplusplus/"
    author = "Conan Community"
    license = "LGPL"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("conan", "libsigcpp", "callback")
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "build_executable": [True, False], "disable_deprecated": [True, False]}
    default_options = {"shared": False, "fPIC": True, "build_executable": True, "disable_deprecated": False}
    exports_sources = ["CMakeLists.txt", "0001-libsigcpp.patch"]
    generators = "cmake"
    no_copy_source = True

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libsigc++-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SIGCXX_DISABLE_DEPRECATED"] = False
        cmake.definitions["SIGCXX_BUILD_TESTS"] = False
        cmake.definitions["SIGCXX_BUILD_EXAMPLES"] = False
        cmake.definitions['CMAKE_INSTALL_INCLUDEDIR'] = 'include'
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        with tools.chdir(self.source_folder):
            tools.patch(base_path=self._source_subfolder, patch_file="0001-libsigcpp.patch")
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_id(self):
        self.info.header_only()
