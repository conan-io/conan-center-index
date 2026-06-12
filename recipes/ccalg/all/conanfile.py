from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0"


class CcalgConan(ConanFile):
    name = "ccalg"
    license = "BSD-3-Clause"
    author = "CandyMi"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ccalg.dev"
    description = (
        "A header-only library for high-performance data structures in C/C++. "
        "Provides intrusive red-black tree (ccmap), hashmap (cchashmap), "
        "doubly/singly linked lists (cclist/cclink), d-ary heap (ccheap), "
        "dynamic array (ccvector), sorted-array map (ccflatmap), "
        "treap with order statistics (cctreap), and UTF-8 codec (ccunicode). "
        "Compatible with C89/C99/C++/MSVC. Zero internal node allocation."
    )
    topics = ("data-structures", "header-only", "intrusive", "c", "c-plus-plus")
    package_type = "header-library"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True)

    def package(self):
        copy(self, "include/*.h", src=self.source_folder,
            dst=os.path.join(self.package_folder, "include"),
            keep_path=False)
        copy(self, "LICENSE", src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Users include as <ccmap.h> or <ccalg/ccmap.h>
        self.cpp_info.includedirs = ["include"]

        self.cpp_info.set_property("cmake_file_name", "ccalg")
        self.cpp_info.set_property("cmake_target_name", "ccalg::ccalg")
