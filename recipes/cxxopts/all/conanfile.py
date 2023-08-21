from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.51.1"


class CxxOptsConan(ConanFile):
    name = "cxxopts"
    homepage = "https://github.com/jarro2783/cxxopts"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Lightweight C++ option parser library, supporting the standard GNU style syntax for options."
    license = "MIT"
    topics = ("option-parser", "positional-arguments ", "header-only")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "unicode": [True, False],
    }
    default_options = {
        "unicode": False,
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "14",
            "msvc": "190",
            "gcc": "4.9",
            "clang": "3.9",
            "apple-clang": "8",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.unicode:
            self.requires("icu/72.1")

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

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "cxxopts.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cxxopts")
        self.cpp_info.set_property("cmake_target_name", "cxxopts::cxxopts")
        self.cpp_info.set_property("pkg_config_name", "cxxopts")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.unicode:
            self.cpp_info.defines = ["CXXOPTS_USE_UNICODE"]
