import os
from conans import ConanFile, tools


class Toml11Conan(ConanFile):
    name = "toml11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ToruNiina/toml11"
    description = "TOML for Modern C++"
    topics = ("toml", "c-plus-plus-11", "c-plus-plus", "parser", "serializer")
    license = "MIT"
    no_copy_source = True

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("*.hpp", dst="include/toml11", src=self._source_subfolder)
        self.copy("*.hpp",
                  dst="include/toml11/toml",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.info.header_only()
