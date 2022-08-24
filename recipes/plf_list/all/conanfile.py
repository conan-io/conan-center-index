from conans import ConanFile, tools

required_conan_version = ">=1.33.0"


class PlflistConan(ConanFile):
    name = "plf_list"
    description = "plf::list is a drop-in higher-performance replacement for std::list"
    license = "Zlib"
    topics = ("plf_list", "container", "linked-list", "list")
    homepage = "https://github.com/mattreecebentley/plf_list"
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
        self.copy("plf_list.h", dst="include", src=self._source_subfolder)
