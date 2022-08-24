import os
from conan import ConanFile, tools

required_conan_version = ">=1.33.0"

class TinydirConan(ConanFile):
    name = "tinydir"
    description = "Lightweight, portable and easy to integrate C directory and file reader"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cxong/tinydir"
    topics = ("portable", "filesystem", "directory", "posix", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("tinydir.h", dst="include", src=self._source_subfolder)
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
