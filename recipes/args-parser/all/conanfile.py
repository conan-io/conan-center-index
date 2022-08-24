from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class ArgsParserConan(ConanFile):
    name = "args-parser"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/args-parser"
    license = "MIT"
    description = "Small C++ header-only library for parsing command line arguments."
    topics = ("args-parser", "argument", "parsing")
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
            tools.build.check_min_cppstd(self, self, "14")

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
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "args-parser"), dst=os.path.join("include", "args-parser"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "args-parser"
        self.cpp_info.names["cmake_find_package_multi"] = "args-parser"
        self.cpp_info.includedirs.append(os.path.join("include", "args-parser"))
