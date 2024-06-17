from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class SpanLiteConan(ConanFile):
    name = "span-lite"
    description = "A C++20-like span for C++98, C++11 and later in a single-file header-only library"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/span-lite"
    topics = ("cpp98", "cpp11", "cpp14", "cpp17", "span", "span-implementations", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "span-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::span-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "span-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "span-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["spanlite"].names["cmake_find_package"] = "span-lite"
        self.cpp_info.components["spanlite"].names["cmake_find_package_multi"] = "span-lite"
        self.cpp_info.components["spanlite"].set_property("cmake_target_name", "nonstd::span-lite")
        self.cpp_info.components["spanlite"].libdirs = []
        self.cpp_info.components["spanlite"].resdirs = []
