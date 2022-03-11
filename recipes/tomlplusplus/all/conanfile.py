from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os


class TomlPlusPlusConan(ConanFile):
    name = "tomlplusplus"
    homepage = "https://github.com/marzer/tomlplusplus"
    description = "Header-only TOML config file parser and serializer for modern C++."
    topics = ("conan", "tomlformoderncpp", "toml++", "tomlplusplus",
              "toml", "json", "header-only", "single-header")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = ("compiler",)
    options = {"multiple_headers": [True, False, "deprecated"]}
    default_options = {"multiple_headers": "deprecated"}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16" if tools.Version(self.version) < "2.2.0" else "15",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if self.options.multiple_headers != "deprecated":
            self.output.warn("The {} option 'multiple_headers' has been deprecated. Both formats are in the same package.")

        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires c++17 support. The current compiler {} {} does not support it.".format(
                    self.name, self.settings.compiler, self.settings.compiler.version))

        if self.settings.compiler == "apple-clang" and tools.Version(self.version) < "2.3.0":
            raise ConanInvalidConfiguration("The current compiler {} {} is supported in version >= 2.3.0".format(
                    self.settings.compiler, self.settings.compiler.version))
        
        if self.settings.compiler == "Visual Studio":
            if tools.Version(self.version) == "2.1.0":
                raise ConanInvalidConfiguration("The current compiler {} {} is unable to build version 2.1.0".format(
                        self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], 
                  destination=self._source_subfolder, strip_root=True) 

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h**", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="toml.hpp", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
