from conan import ConanFile
from conan.tools.build import check_min_cstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.1"

class ResultLibConan(ConanFile):
    name = "resultlib"
    description = "Elegant error handling in C"
    license = "Apache-2.0"
    homepage = "https://result.guillermo.dev/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("header-only", "error-handling", "c-library", "declarative-programming", "monadic-interface", "result")
    package_type = "header-library"
    no_copy_source = True

    languages = ["C"]
    implements = ["auto_header_only"]

    def layout(self):
        basic_layout(self, src_folder="src")
    
    def validate(self):
        if self.settings.get_safe("compiler.cstd"):
            check_min_cstd(self, 23)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "result.h", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "include", "resultlib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
