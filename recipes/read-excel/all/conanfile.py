from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os
import textwrap


class ReadExcelConan(ConanFile):
    name = "read-excel"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/read-excel"
    license = "MIT"
    description = "This is very simple implementation of the Excel 97-2003 format (BIFF8) written in C++. Supported reading only."
    topics = ("read", "excel", "biff8")
    settings = "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "10"
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "14")

        compiler = str(self.settings.compiler)
        if compiler not in self._compilers_minimum_version:
            self.output.warn("Unknown compiler, assuming it supports at least C++14")
            return

        version = tools.scm.Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration("args-parser requires a compiler that supports at least C++14")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "read-excel"), dst=os.path.join("include", "read-excel"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "read-excel"
        self.cpp_info.names["cmake_find_package_multi"] = "read-excel"
        self.cpp_info.includedirs.append(os.path.join("include", "read-excel"))
