from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class OptionalLiteConan(ConanFile):
    name = "optional-lite"
    description = "A single-file header-only version of a C++17-like optional, a nullable object for C++98, C++11 and later"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/optional-lite"
    topics = ("cpp98", "cpp17", "optional", "optional-implementations", "header-only")
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
        self.cpp_info.set_property("cmake_file_name", "optional-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::optional-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "optional-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "optional-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["optionallite"].names["cmake_find_package"] = "optional-lite"
        self.cpp_info.components["optionallite"].names["cmake_find_package_multi"] = "optional-lite"
        self.cpp_info.components["optionallite"].set_property("cmake_target_name", "nonstd::optional-lite")
        self.cpp_info.components["optionallite"].bindirs = []
        self.cpp_info.components["optionallite"].libdirs = []
