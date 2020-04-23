from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class TomlPlusPlusConan(ConanFile):
    name = "toml++"
    homepage = "https://github.com/marzer/tomlplusplus"
    description = "Header-only TOML config file parser and serializer for modern C++."
    topics = ("conan", "tomlformoderncpp", "toml++", "tomlplusplus",
              "toml", "json", "header-only", "single-header")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    options = {
        "multiple_headers": [True, False]
    }
    default_options = {
        "multiple_headers": False
    }
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")
        compilers = {"gcc": "7", "clang": "5",
                     "Visual Studio": "15", "apple-clang": "10"}
        min_version = compilers.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires c++17 support. The current compiler {} {} does not support it.".format(
                    self.name, self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.options.multiple_headers:
            header_dir = os.path.join(
                self._source_subfolder, "include", "toml++")
            self.copy(pattern="*.h", dst="include", src=header_dir)
        else:
            self.copy(pattern="toml.hpp", dst="include",
                      src=self._source_subfolder)
