import os
from conans import ConanFile, tools


class SpyConan(ConanFile):
    name = "spy"
    version = "0.0.3"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jfalcou.github.io/spy/"
    description = "C++ 17 for constexpr-proof detection and classification of informations about OS, compiler, etc..."
    topics = ("c++17", "config", "metaprogramming")
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*.hpp", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
