import os
from conans import ConanFile, tools


class CppcodecConan(ConanFile):
    name = "cppcodec"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tplgy/cppcodec"
    description = "Header-only C++11 library to encode/decode base64, base64url, base32, base32hex and hex (a.k.a. base16) as specified in RFC 4648, plus Crockford's base32"
    topics = ("base64", "cpp11", "codec", "base32")
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*hpp", dst=os.path.join("include", "cppcodec"), src=os.path.join(self._source_subfolder, "cppcodec"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

