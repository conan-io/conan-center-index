from conan import ConanFile, tools

required_conan_version = ">=1.33.0"


class PdqsortConan(ConanFile):
    name = "pdqsort"
    description = "Pattern-defeating quicksort."
    license = "Zlib"
    topics = ("conan", "pdqsort", "sort")
    homepage = "https://github.com/orlp/pdqsort"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        self.copy("pdqsort.h", dst="include", src=self._source_subfolder)
