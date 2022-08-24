import os

from conan import ConanFile, tools

required_conan_version = ">=1.33.0"

class FastcppcsvparserConan(ConanFile):
    name = "fast-cpp-csv-parser"
    description = "C++11 header-only library for reading comma separated value (CSV) files."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ben-strasser/fast-cpp-csv-parser"
    topics = ("csv", "parser", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {"with_thread": [True, False]}
    default_options = {"with_thread": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("csv.h", dst=os.path.join("include", "fast-cpp-csv-parser"), src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = ["include", os.path.join("include", "fast-cpp-csv-parser")]
        if not self.options.with_thread:
            self.cpp_info.defines.append("CSV_IO_NO_THREAD")
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.with_thread:
            self.cpp_info.system_libs.append("pthread")
