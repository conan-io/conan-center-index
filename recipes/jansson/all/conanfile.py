#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class JanssonConan(ConanFile):
    name = "jansson"
    description = "C library for encoding, decoding and manipulating JSON data"
    topics = ("conan", "jansson", "json", "encoding", "decoding", "manipulation")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.digip.org/jansson/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_urandom": [True, False],
        "use_windows_cryptoapi": [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'use_urandom': True,
        'use_windows_cryptoapi': True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["JANSSON_BUILD_DOCS"] = False
        cmake.definitions["JANSSON_BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["JANSSON_EXAMPLES"] = False
        cmake.definitions["JANSSON_WITHOUT_TESTS"] = True
        cmake.definitions["USE_URANDOM"] = self.options.use_urandom
        cmake.definitions["USE_WINDOWS_CRYPTOAPI"] = self.options.use_windows_cryptoapi

        if self.settings.compiler == "Visual Studio":
            if "MT" in self.settings.compiler.runtime:
                cmake.definitions["JANSSON_STATIC_CRT"] = True

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # drop pc and cmake file
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'cmake'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
