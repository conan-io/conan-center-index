from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class XpackConan(ConanFile):
    name = "xpack"
    description = "C++ reflection, ability to convert between C++ structures and json/xml."
    topics = ("xpack", "json", "reflection", "xml")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xyz347/xpack"
    license = "Apache-2.0"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*[.h|.hpp]", dst=os.path.join("include", "xpack"), excludes=["example/*", "gtest/*"], src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
