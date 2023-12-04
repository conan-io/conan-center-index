from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class Md4QtConan(ConanFile):
    name = "md4qt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/md4qt"
    license = "MIT"
    description = "Header-only C++ library for parsing Markdown."
    topics = ("markdown", "gfm", "parser", "icu", "ast", "commonmark", "md", "qt6", "stl", "cpp17")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "191",
            "gcc": "9",
            "clang": "12",
            "apple-clang": "14",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("icu/74.1")
        self.requires("uriparser/0.9.7")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "md4qt"), dst=os.path.join(self.package_folder, "include", "md4qt"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "md4qt")
        self.cpp_info.set_property("cmake_target_name", "md4qt::md4qt")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
