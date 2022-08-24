from conan import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class RapidjsonConan(ConanFile):
    name = "rapidjson"
    description = "A fast JSON parser/generator for C++ with both SAX/DOM style API"
    topics = ("conan", "rapidjson", "json", "parser", "generator")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://rapidjson.org"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
       tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="license.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "RapidJSON"
        self.cpp_info.names["cmake_find_package_multi"] = "RapidJSON"
