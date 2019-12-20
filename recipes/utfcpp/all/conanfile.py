import os
from conans import ConanFile, tools


class UtfCppConan(ConanFile):
    name = "utfcpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nemtrif/utfcpp"
    description = "UTF-8 with C++ in a Portable Way"
    topics = ("utf", "utf8", "unicode", "text")
    license = "BSL-1.0"
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.h",
                  dst="include",
                  src=os.path.join(self._source_subfolder, "source"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.info.header_only()