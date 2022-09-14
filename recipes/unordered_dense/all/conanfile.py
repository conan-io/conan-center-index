from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.51.3"


class PackageConan(ConanFile):
    name = "unordered_dense"
    description = "A fast & densely stored hashmap and hashset based on robin-hood backward shift deletion"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinus/unordered_dense"
    topics = ("unordered_map", "unordered_set", "hashmap", "hashset", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "msvc": "1914",
            "gcc": "7",
            "clang": "7",
            "apple-clang": "11",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.info.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if minimum_version and Version(self.info.settings.get_safe("compiler.version")) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include", "ankerl"), src=os.path.join(self.source_folder, "include", "ankerl"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        self.cpp_info.set_property("cmake_file_name", "unordered_dense")
        self.cpp_info.set_property("cmake_target_name", "unordered_dense::unordered_dense")
        self.cpp_info.set_property("pkg_config_name", "package")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "unordered_dense"
        self.cpp_info.filenames["cmake_find_package_multi"] = "unordered_dense"
        self.cpp_info.names["cmake_find_package"] = "unordered_dense"
        self.cpp_info.names["cmake_find_package_multi"] = "unordered_dense"
