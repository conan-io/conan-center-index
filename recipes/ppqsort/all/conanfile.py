from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd

import os

required_conan_version = ">=2.9.0"


class PPQSortConan(ConanFile):
    name = "ppqsort"
    package_type = "header-library"

    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/GabTux/PPQSort"
    description = "Parallel Pattern Quicksort"
    topics = ("algorithms", "sorting", "parallel", "header-only")

    settings = "compiler", "os"  # keep it for checking standard and linking pthread
    implements = ["auto_header_only"]
    no_copy_source = True
    languages = "C++"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "include/*", self.source_folder, self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_target_name", "PPQSort::PPQSort")
        self.cpp_info.set_property("cmake_file_name", "PPQSort")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
