from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"


class Jpcre2Conan(ConanFile):
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
        self.requires("pcre2/10.37")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("jpcre2.hpp", dst="include", src=os.path.join(self._source_subfolder, "src"))

    def package_id(self):
        self.info.header_only()
