from conans import ConanFile, tools
import os


class AudiofileConan(ConanFile):
    name = "audiofile"
    description = "A simple C++11 library for reading and writing audio files."
    topics = ("conan", "audiofile", "audio", "file-format", "wav", "aif")
    license = "MIT"
    homepage = "https://github.com/adamstark/AudioFile"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 11)
        if tools.scm.Version(self.version) < "1.1.0":
            self.license = "GPL-3.0-or-later"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("AudioFile-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("AudioFile.h", dst="include", src=self._source_subfolder)
