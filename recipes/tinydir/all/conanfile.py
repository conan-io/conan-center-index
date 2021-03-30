import os
from conans import ConanFile, tools


class TinydirConan(ConanFile):
    name = "tinydir"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cxong/tinydir"
    description = "Lightweight, portable and easy to integrate C directory and file reader"
    topics = ("conan", "c", "portable", "filesystem", "directory", "posix", "header-only")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("tinydir.h", dst="include", src=self._source_subfolder)
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
