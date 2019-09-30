#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools


class Asio(ConanFile):
    name = "asio"
    
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://think-async.com/Asio"
    description = "Asio is a cross-platform C++ library for network and low-level I/O"
    topics = ("conan", "asio", "network", "io", "low-level")
    license = "BSL-1.0"

    settings = "os", "arch", "compiler", "build_type"

    no_copy_source = True
    _source_subfolder = "source_subfolder"

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
        self.cpp_info.defines.append('ASIO_STANDALONE')
        if tools.os_info.is_linux:
            self.cpp_info.libs.append('pthread')

    def package_id(self):
        self.info.header_only()
