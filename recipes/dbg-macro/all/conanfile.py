import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class DbgMacroConan(ConanFile):
    name = "dbg-macro"
    description = "A dbg(...) macro for C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sharkdp/dbg-macro"
    topics = ("debugging", "macro", "pretty-printing", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17
 
    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15.7",
            "msvc": "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()
 
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"): 
            check_min_cppstd(self, self._min_cppstd)
 
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(f"{self.name} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "dbg.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
