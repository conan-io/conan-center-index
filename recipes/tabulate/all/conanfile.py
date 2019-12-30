#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools


class Tabulate(ConanFile):
    name = "tabulate"
    
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/tabulate"
    description = "Table Maker for Modern C++"
    author = "Pranav"
    topics = ("conan", "cpp17", "table", "table-maker", "formatted-text", "terminal", "cli")
    license = "MIT"
    no_copy_source = True
    settings = "compiler"
    
    _source_subfolder = "source_subfolder"

    def configure(self):
        tools.check_min_cppstd(self, "17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.info.header_only()
