from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy, replace_in_file
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

    implements = ["auto_header_only"]
    settings = "os", "arch", "compiler"
    languages = "C++"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        basic_layout(self)

    def build(self):
        # Patch to fix missing include for hardware_constructive_interference_size on libc++
        replace_in_file(self, os.path.join(self.source_folder, "include", "ppqsort", "parameters.h"),
                        "#include <execution>", "#include <execution>\n#include <new>")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "include/*", self.source_folder, self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_target_name", "PPQSort::PPQSort")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
