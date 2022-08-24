import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class SourceLocationConan(ConanFile):
    name = "source_location"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Rechip/source_location"
    description = "source_location header for some older compilers"
    topics = ("cpp", "source_location", "header-only")
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
            "Visual Studio": "16.6",
            "gcc": "7.1",
            "clang": "9",
            "apple-clang": "12",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "11")
        minimum_version = self._minimum_compilers_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "source_location requires C++11. Your compiler is unknown. Assuming it supports C++11 and required functionality.")
        elif tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "source_location requires C++11 and some embedded functionality, which your compiler does not support.")

    def package_id(self):
        self.info.header_only()
