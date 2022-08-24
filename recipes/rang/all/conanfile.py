from conans import ConanFile, Meson, tools
import os


class RangConan(ConanFile):
    name = "rang"
    description = "A Minimal, Header only Modern c++ library for colors in your terminal"
    homepage = "https://github.com/agauniyal/rang"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Unlicense"
    topics = ("conan", "cli", "colors", "terminal", "console")
    no_copy_source = True
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", src=self._source_subfolder)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
