from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class Rectpack2dConan(ConanFile):
    name = "rectpack2d"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/TeamHypersomnia/rectpack2D"
    description = "C++17 rectangle packing library"
    topics = ("header-only", "rectpack2d", "graphical", "cpp17")
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _min_compilers_version(self):
        return {
            "Visual Studio": "15.7",
            "msvc": "191",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        min_version = self._min_compilers_version.get(str(self.settings.compiler), False)
        if min_version and loose_lt_semver(str(self.settings.compiler.version), min_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include", "rectpack2d"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
