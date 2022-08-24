import os

from conans import ConanFile, tools

class Minimp3Conan(ConanFile):
    name = "minimp3"
    description = "Minimalistic MP3 decoder single header library."
    license = "CC0-1.0"
    topics = ("conan", "minimp3", "decoder", "mp3", "header-only")
    homepage = "https://github.com/lieff/minimp3"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = "minimp3-" + os.path.splitext(os.path.basename(url))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="minimp3*.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
