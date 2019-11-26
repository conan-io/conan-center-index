from conans import ConanFile, tools

import os

class PicoJSONConan(ConanFile):
    name = "picojson"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kazuho/picojson"
    description = "A C++ JSON parser/serializer"
    topics = ("picojson", "json", "header-only", "conan-recipe")

    no_copy_source = True
    _source_subdir_name = "source_subdir"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("picojson-{}".format(self.version), self._source_subdir_name)

    def package(self):
        self.copy("{}.h".format(self.name), dst="include", src=self._source_subdir_name)
        self.copy("LICENSE", dst="licenses", src=self._source_subdir_name)

    def package_info(self):
        self.info.header_only()
