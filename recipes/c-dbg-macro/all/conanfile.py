from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=1.50.0"


class DbgMacroConan(ConanFile):
    name = "c-dbg-macro"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eerimoq/dbg-macro"
    license = "MIT"
    description = "A dbg(...) macro for C"
    topics = ("debugging", "macro", "pretty-printing", "header-only")
    package_type = "header-library"
    settings = ("compiler",  "build_type", "os", "arch")
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("This library is not compatible with Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "dbg.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
