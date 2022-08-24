from conans import ConanFile, tools
import os

required_conan_version = ">=1.33.0"


class RapidcsvConan(ConanFile):
    name = "rapidcsv"
    description = "C++ CSV parser library"
    topics = ("csv", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/d99kris/rapidcsv"
    license = "BSD-3-Clause"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="rapidcsv.h", dst="include", src=os.path.join(self._source_subfolder, "src"))

    def package_id(self):
        self.info.header_only()
