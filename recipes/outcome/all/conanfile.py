import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2"


class OutcomeConan(ConanFile):
    name = "outcome"
    description = "Provides very lightweight outcome<T> and result<T>"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/outcome"
    topics = ("result", "header-only")
    package_type = "header-library"
    settings = "compiler"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "Licence.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "outcome.hpp", src=os.path.join(self.source_folder, "single-header"),
                                  dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
