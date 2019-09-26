#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class Asio(ConanFile):
    name = "asio"
    
    url = "https://github.com/chriskohlhoff/asio"
    homepage = "http://think-async.com/Asio"
    description = "Asio is a cross-platform C++ library for network and low-level I/O"
    topics = ("conan", "asio", "network", "io", "low-level")
    license = "BSL-1.0"

    options = {
        "standalone": [True, False],
        "with_boost_regex": [True, False],
        "with_openssl": [True, False]
    }
    default_options = {
        "standalone": True,
        "with_boost_regex": False,
        "with_openssl": False
    }

    settings = "os"

    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def configure(self):
        if self.options.standalone and self.options.with_boost_regex:
            raise ConanInvalidConfiguration("'standalone' and 'with_boost_regex' are mutually exclusive! Please disable one of them.")

    def requirements(self):
        if self.options.with_boost_regex:
            self.requires.add("boost/1.69.0")

        if self.options.with_openssl:
            self.requires.add("openssl/1.0.2t")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        archive_name = "asio-" + self.version.replace(".", "-")
        extracted_name = "asio-" + archive_name
        os.rename(extracted_name, self._source_subfolder)

    def package(self):
        root_dir = os.path.join(self._source_subfolder, self.name)
        include_dir = os.path.join(root_dir, "include")
        self.copy(pattern="LICENSE_1_0.txt", dst="licenses", src=root_dir)
        self.copy(pattern="*.hpp", dst="include", src=include_dir)
        self.copy(pattern="*.ipp", dst="include", src=include_dir)

    def package_info(self):
        if self.options.standalone:
            self.cpp_info.defines.append('ASIO_STANDALONE')
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')

    def package_id(self):
        self.info.header_only()
