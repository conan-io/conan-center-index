#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools

class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    url = "https://github.com/libsigcplusplus/libsigcplusplus"
    homepage = "https://libsigcplusplus.github.io/libsigcplusplus/"
    license = "LGPL"
    description = "Typesafe callback framework for C++"
    topics = ("libsigcpp", "callback")
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False],"fPIC": [True, False] }
    default_options = {"shared": True }
    exports_sources = ["CMakeLists.txt", "config.h.cmake", "sigc++config.h.cmake"]
    generators = "cmake"
    no_copy_source = True

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libsigc++-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['LIBSIGCPP_BUILD_SHAREDLIB'] = self.options.shared
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.shared:
            self.cpp_info.defines.append('SIGC_DLL')