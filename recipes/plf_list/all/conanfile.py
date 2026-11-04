from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.50.0"


class PlflistConan(ConanFile):
    name = "plf_list"
    description = "plf::list is a drop-in higher-performance replacement for std::list"
    license = "Zlib"
    topics = ("container", "linked-list", "list", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mattreecebentley/plf_list"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "9",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if Version(self.version) >= "2.70":
            if self.settings.compiler.get_safe("cppstd"):
                check_min_cppstd(self, self._min_cppstd)
            minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "plf_list.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
