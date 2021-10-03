from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class TomlPlusPlusConan(ConanFile):
    name = "jpcre2"
    homepage = "https://github.com/jpcre2/jpcre2"
    description = "Header-only C++ wrapper for PCRE2 library."
    topics = ("conan", "regex", "pcre2", "header-only", "single-header")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD"
    settings = list()
    options = {}
    default_options = {}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("pcre2/[>=10.21]")

    def configure(self):
        pass

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("jpcre2.hpp", dst="include", src=os.path.join(self._source_subfolder, "src"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "jpcre2"
        self.cpp_info.names["cmake_find_package_multi"] = "jpcre2"
