from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class MgsConan(ConanFile):
    name = "mgs"
    url = "https://github.com/conan-io/conan-center-index"
    description = "C++14 codec library"
    homepage = "https://theodelrieu.github.io/mgs-docs"
    license = "MIT"
    topics = ("codec", "base64", "base32", "base16")
    settings = "compiler"
    _source_subfolder = "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "3.4",
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 14)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("mgs requires C++14, which your compiler does not fully support.")
        else:
            self.output.warn("mgs requires C++14. Your compiler is unknown. Assuming it supports C++14.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name, self._source_subfolder)

    def package(self):
        self.copy("*", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "mgs"
        self.cpp_info.names["cmake_find_package_multi"] = "mgs"

        self.cpp_info.components["mgs-config"].names["cmake_find_package"] = "config"
        self.cpp_info.components["mgs-config"].names["cmake_find_package_multi"] = "config"

        self.cpp_info.components["mgs-meta"].names["cmake_find_package"] = "meta"
        self.cpp_info.components["mgs-meta"].names["cmake_find_package"] = "meta"
        self.cpp_info.components["mgs-meta"].requires = ["mgs-config"]

        self.cpp_info.components["mgs-exceptions"].names["cmake_find_package"] = "exceptions"
        self.cpp_info.components["mgs-exceptions"].names["cmake_find_package_multi"] = "exceptions"
        self.cpp_info.components["mgs-exceptions"].requires = ["mgs-config"]

        self.cpp_info.components["mgs-codecs"].names["cmake_find_package"] = "codecs"
        self.cpp_info.components["mgs-codecs"].names["cmake_find_package_multi"] = "codecs"
        self.cpp_info.components["mgs-codecs"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions"]

        self.cpp_info.components["mgs-base_n"].names["cmake_find_package"] = "base_n"
        self.cpp_info.components["mgs-base_n"].names["cmake_find_package_multi"] = "base_n"
        self.cpp_info.components["mgs-base_n"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs"]

        self.cpp_info.components["mgs-base16"].names["cmake_find_package"] = "base16"
        self.cpp_info.components["mgs-base16"].names["cmake_find_package_multi"] = "base16"
        self.cpp_info.components["mgs-base16"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        self.cpp_info.components["mgs-base32"].names["cmake_find_package"] = "base32"
        self.cpp_info.components["mgs-base32"].names["cmake_find_package_multi"] = "base32"
        self.cpp_info.components["mgs-base32"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        self.cpp_info.components["mgs-base64"].names["cmake_find_package"] = "base64"
        self.cpp_info.components["mgs-base64"].names["cmake_find_package_multi"] = "base64"
        self.cpp_info.components["mgs-base64"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        self.cpp_info.components["mgs-base64url"].names["cmake_find_package"] = "base64url"
        self.cpp_info.components["mgs-base64url"].names["cmake_find_package_multi"] = "base64url"
        self.cpp_info.components["mgs-base64url"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]

        self.cpp_info.components["mgs-base32hex"].names["cmake_find_package"] = "base32hex"
        self.cpp_info.components["mgs-base32hex"].names["cmake_find_package_multi"] = "base32hex"
        self.cpp_info.components["mgs-base32hex"].requires = ["mgs-config", "mgs-meta", "mgs-exceptions", "mgs-codecs", "mgs-base_n"]
