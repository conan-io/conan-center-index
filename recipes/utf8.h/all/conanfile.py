import os
import re
from conans import ConanFile, tools


class Utf8HConan(ConanFile):
    name = "utf8.h"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sheredom/utf8.h"
    description = "Single header utf8 string functions for C and C++"
    topics = ("utf8", "unicode", "text")
    license = "Unlicense"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]['url']
        m = re.match(r'.*/([0-9a-f]+)\.tar.gz', url)
        extracted_dir = self.name + "-" + m[1]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("utf8.h", dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
