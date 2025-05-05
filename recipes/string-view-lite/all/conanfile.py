from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class StringViewLite(ConanFile):
    name = "string-view-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/string-view-lite"
    description = "string-view lite - A C++17-like string_view for C++98, C++11 and later in a single-file header-only library"
    topics = ("cpp98", "cpp11", "cpp14", "cpp17", "string-view", "string-view-implementations")
    license = "BSL-1.0"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "string-view-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::string-view-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "string-view-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "string-view-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["stringviewlite"].names["cmake_find_package"] = "string-view-lite"
        self.cpp_info.components["stringviewlite"].names["cmake_find_package_multi"] = "string-view-lite"
        self.cpp_info.components["stringviewlite"].set_property("cmake_target_name", "nonstd::string-view-lite")
        self.cpp_info.components["stringviewlite"].bindirs = []
        self.cpp_info.components["stringviewlite"].libdirs = []
