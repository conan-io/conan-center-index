from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.51.3"


class EternalConan(ConanFile):
    name = "eternal"
    description = "A C++14 compile-time/constexpr map and hash map with minimal binary footprint"
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mapbox/eternal"
    topics = ("hashing", "map", "constexpr", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "1910",
            "gcc": "5",
            "clang": "4",
            "apple-clang": "10",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.get_safe("compiler.version")) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
