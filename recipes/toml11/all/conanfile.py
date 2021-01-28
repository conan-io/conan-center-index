import os
from conans import ConanFile, tools


class Toml11Conan(ConanFile):
    name = "toml11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ToruNiina/toml11"
    description = "TOML for Modern C++"
    topics = ("toml", "c-plus-plus-11", "c-plus-plus", "parser", "serializer")
    license = "MIT"
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
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("toml.hpp", dst=os.path.join("include", "toml11"), src=self._source_subfolder)
        self.copy("*.hpp", dst=os.path.join("include", "toml11", "toml"), src=os.path.join(self._source_subfolder, "toml"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "toml11"))
