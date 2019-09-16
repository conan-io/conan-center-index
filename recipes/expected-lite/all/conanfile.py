#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools


class ExpectedLite(ConanFile):
    name = "expected-lite"
    
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/expected-lite"
    description = "expected lite - Expected objects in C++11 and later in a single-file header-only library"
    author = "Martin Moene"
    topics = ("conan", "cpp98", "cpp11", "cpp14", "cpp17", "expected", "expected-implementations")
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
