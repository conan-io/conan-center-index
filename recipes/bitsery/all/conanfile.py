import os

from conans import ConanFile, tools


class BitseryConan(ConanFile):
    name = "bitsery"
    description = "Header only C++ binary serialization library. It is designed around the networking requirements for real-time data delivery, especially for games."
    topics = "serialization", "binary", "header-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fraillt/bitsery"
    license = "MIT"
    settings = "compiler", "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "bitsery-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst=os.path.join("include", "bitsery"), src=os.path.join(self._source_subfolder, "include", "bitsery"))

    def package_id(self):
        self.info.header_only()
