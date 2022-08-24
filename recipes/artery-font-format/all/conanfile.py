from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"


class ArteryFontFormatConan(ConanFile):
    name = "artery-font-format"
    license = "MIT"
    homepage = "https://github.com/Chlumsky/artery-font-format"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Artery Atlas Font format library"
    topics = ("artery", "font", "atlas")

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=self._source_subfolder, dst="include")
        self.copy("*.hpp", src=self._source_subfolder, dst="include")
