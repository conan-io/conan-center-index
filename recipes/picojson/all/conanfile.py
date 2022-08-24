from conan import ConanFile, tools
import os, glob


class PicoJSONConan(ConanFile):
    name = "picojson"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kazuho/picojson"
    description = "A C++ JSON parser/serializer"
    topics = ("picojson", "json", "header-only", "conan-recipe")
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(glob.glob("picojson-*")[0], self._source_subfolder)

    def package(self):
        self.copy("{}.h".format(self.name), dst="include", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.info.header_only()
