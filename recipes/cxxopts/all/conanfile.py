from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
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
            "gcc": "5",
            "clang": "3.9",
            "apple-clang": "8",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.unicode:
            self.requires("icu/71.1")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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
