import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class DbgMacroConan(ConanFile):
    name = "dbg-macro"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sharkdp/dbg-macro"
    license = "MIT"
    description = "A dbg(...) macro for C++"
    topics = ("conan", "debugging", "macro", "pretty-printing", "header-only")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("dbg.h", dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
