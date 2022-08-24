from conans import ConanFile, tools

required_conan_version = ">=1.33.0"


class PlfcolonyConan(ConanFile):
    name = "plf_colony"
    description = "An unordered data container providing fast iteration/insertion/erasure " \
                  "while maintaining pointer/iterator/reference validity to non-erased elements."
    license = "Zlib"
    topics = ("plf_colony", "container", "bucket", "unordered")
    homepage = "https://github.com/mattreecebentley/plf_colony"
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
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("plf_colony.h", dst="include", src=self._source_subfolder)
