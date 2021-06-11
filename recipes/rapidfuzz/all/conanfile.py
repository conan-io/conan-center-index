from conans import ConanFile, tools
import glob


class RapidFuzzConan(ConanFile):
    name = "rapidfuzz"
    description = "Rapid fuzzy string matching in C++ using the Levenshtein Distance "
    topics = ("conan", "cpp", "levenshtein", "string-matching", "string-similarity", "string-comparison")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/maxbachmann/rapidfuzz-cpp"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        tools.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="rapidfuzz/*.hpp", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
