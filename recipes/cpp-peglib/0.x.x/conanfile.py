import os

from conans import ConanFile, tools

class CpppeglibConan(ConanFile):
    name = "cpp-peglib"
    description = "A single file C++11 header-only PEG (Parsing Expression Grammars) library."
    license = "MIT"
    topics = ("conan", "cpp-peglib", "peg", "parser", "header-only")
    homepage = "https://github.com/yhirose/cpp-peglib"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("peglib.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
