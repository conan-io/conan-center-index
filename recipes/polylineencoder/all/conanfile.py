#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class PolylineencoderConan(ConanFile):
    name = "polylineencoder"
    description = "Google Encoded Polyline Algorithm Format library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vahancho/polylineencoder"
    author = "vahancho"
    license = "MIT"
    topics = ("conan", "gepaf", "encoded-polyline", "google-polyline", "polyline")
    settings = "os", "arch", "compiler", "build_type"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)
        tools.replace_in_file(self._source_subfolder + "/src/polylineencoder.cpp", "#include <cmath>",
        '''#include <cmath>
           #include <limits>''')

    def build(self):
        c = CMake(self)
        c.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        c.build()
        c.test()

    def package(self):
        self.copy("*.h",   dst="include/" + self.name, keep_path=False)
        self.copy("*.a",   dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.pdb", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs.append(self.name)
