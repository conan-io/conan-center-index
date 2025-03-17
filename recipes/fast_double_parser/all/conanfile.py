from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class FastDoubleParserConan(ConanFile):
    name = "fast_double_parser"
    description = "Fast function to parse strings into double (binary64) floating-point values, enforces the RFC 7159 (JSON standard) grammar: 4x faster than strtod"
    license = ("Apache-2.0", "BSL-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lemire/fast_double_parser"
    topics = ("numerical", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        include_folder = os.path.join(self.source_folder, "include")
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=include_folder)
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
