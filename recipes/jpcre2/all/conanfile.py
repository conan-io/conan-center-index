from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class TomlPlusPlusConan(ConanFile):
    name = "jpcre2"
    homepage = "https://github.com/jpcre2/jpcre2"
    description = "Header-only C++ wrapper for PCRE2 library."
    topics = ("regex", "pcre2", "header-only", "single-header")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("pcre2/[>=10.21]")

    def configure(self):
        pass

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("jpcre2.hpp", dst="include", src=os.path.join(self._source_subfolder, "src"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "jpcre2"
        self.cpp_info.names["cmake_find_package_multi"] = "jpcre2"
