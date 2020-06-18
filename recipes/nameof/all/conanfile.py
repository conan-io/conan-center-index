import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class NameofConan(ConanFile):
    name = "nameof"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Neargye/nameof"
    license = "MIT"
    description = "Header-only C++17 library provides nameof macros and functions to simply obtain the name of a variable, type, function, macro, and enum."
    topics = (
        "conan",
        "nameof",
        "cplusplus",
        "enum-to-string",
        "serialization",
        "reflection",
        "header-only",
        "compile-time"
    )
    no_copy_source = True
    settings = "compiler"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _supported_compiler(self):
        compiler = str(self.settings.compiler)
        version = tools.Version(self.settings.compiler.version)
        if compiler == "Visual Studio" and version >= "15":
            return True
        if compiler == "gcc" and version >= "7":
            return True
        if compiler == "clang" and version >= "5":
            return True
        if compiler == "apple-clang" and version >= "9":
            return True
        return False

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if not self._supported_compiler:
            raise ConanInvalidConfiguration("nameof: Unsupported compiler (https://github.com/Neargye/nameof#compiler-compatibility).")

    def package(self):
        self.copy("nameof.hpp", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
