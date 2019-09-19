#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools


class OptionalLite(ConanFile):
    name = "optional-lite"
    
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/optional-lite"
    description = "A single-file header-only version of a C++17-like optional, a nullable object for C++98, C++11 and later"
    author = "Martin Moene"
    topics = ("conan", "cpp98", "cpp17", "optional", "optional-implementations")
    license = "BSL-1.0"
    
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.info.header_only()
