import os

from conans import ConanFile, tools

class FastcppcsvparserConan(ConanFile):
    name = "fast-cpp-csv-parser"
    description = "C++11 header-only library for reading comma separated value (CSV) files."
    license = "BSD-3-Clause"
    topics = ("conan", "fast-cpp-csv-parser", "csv", "parser", "header-only")
    homepage = "https://github.com/ben-strasser/fast-cpp-csv-parser"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler"
    no_copy_source = True
    options = {"with_thread": [True, False]}
    default_options = {"with_thread": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = self.name + "-" + os.path.splitext(os.path.basename(url))[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("csv.h", dst=os.path.join("include", "fast-cpp-csv-parser"), src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs = ["include", os.path.join("include", "fast-cpp-csv-parser")]
        if not self.options.with_thread:
            self.cpp_info.defines.append("CSV_IO_NO_THREAD")
        if self.settings.os == "Linux" and self.options.with_thread:
            self.cpp_info.system_libs.append("pthread")
