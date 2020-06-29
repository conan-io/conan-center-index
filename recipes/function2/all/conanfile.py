import os

from conans import ConanFile, tools


class Function2Conan(ConanFile):
    name = "function2"
    description = "Improved and configurable drop-in replacement to std::function that supports move only types, multiple overloads and more"
    topics = "function", "header-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Naios/continuable"
    license = "Boost Software License 1.0"
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        tools.check_min_cppstd(self, "14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "function2-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include/function2", src=self._source_subfolder + "/include/function2")

    def package_id(self):
        self.info.header_only()
