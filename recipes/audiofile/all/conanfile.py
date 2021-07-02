from conans import ConanFile, tools
import os


class AudiofileConan(ConanFile):
    name = "audiofile"
    description = "A simple C++11 library for reading and writing audio files."
    topics = ("conan", "audiofile", "audio", "file-format", "wav", "aif")
    license = "GPL-3.0-or-later"
    homepage = "https://github.com/adamstark/AudioFile"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("AudioFile-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("AudioFile.h", dst="include", src=self._source_subfolder)
