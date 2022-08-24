from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os


class SMLConan(ConanFile):
    name = "sml"
    homepage = "https://github.com/boost-ext/sml"
    description = "SML: C++14 State Machine Library"
    topics = ("state-machine", "metaprogramming", "design-patterns", "sml")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "14")
        minimum_version = self._minimum_compilers_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "SML requires C++14. Your compiler is unknown. Assuming it supports C++14.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "SML requires C++14, which your compiler does not support.")

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # tools.files.patch(self, patch_file="patches/0001-fix-clang12-error.patch")

    def package(self):
        self.copy(pattern="*", dst="include",
                  src=os.path.join(self._source_subfolder, "include"))
        self.copy("*LICENSE.md", dst="licenses", keep_path=False)

    def package_id(self):
        self.info.header_only()
