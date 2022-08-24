import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class PrettyNameConan(ConanFile):
    name = "pretty-name"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Rechip/pretty-name"
    description = "An easy and consistent way how to get type names in C++"
    topics = ("cpp", "typename")
    settings = ["compiler"]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, "14")
        minimum_version = self._minimum_compilers_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "pretty-name requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "pretty-name requires C++14, which your compiler does not support.")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "pretty-name"
        self.cpp_info.names["cmake_find_package_multi"] = "pretty-name"
