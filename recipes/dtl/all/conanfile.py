from conan import ConanFile, tools$
import os

required_conan_version = ">=1.33.0"

class DtlConan(ConanFile):
    name = "dtl"
    description = "diff template library written by C++"
    topics = ("diff", "library", "algorithm")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cubicdaiya/dtl"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(os.path.join("dtl", "*.hpp"), dst="include", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

