from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.1"

class ResultLibConan(ConanFile):
    name = "resultlib"
    description = "Elegant error handling in C"
    license = "Apache-2.0"
    author = "Guillermo Calvo (guillermo@guillermo.dev)"
    url = "https://github.com/guillermocalvo/resultlib/"
    homepage = "https://result.guillermo.dev/"
    topics = ("header-only", "error-handling", "c-library", "declarative-programming", "monadic-interface", "result")
    exports_sources = "src/result.h"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        src_path = os.path.join(self.source_folder, "src")
        include_path = os.path.join(self.package_folder, os.path.join("include", "resultlib"))
        licenses_path = os.path.join(self.package_folder, "licenses")
        copy(self, "result.h", src_path, include_path)
        copy(self, "LICENSE", self.source_folder, licenses_path)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
