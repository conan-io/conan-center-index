from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class StatusValueLiteConan(ConanFile):
    name = "status-value-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/status-value-lite"
    description = (
        "status-value - A class for status and optional value for C++11 and "
        "later, C++98 variant provided in a single-file header-only library"
    )
    topics = ("cpp98", "cpp11", "cpp14", "cpp17", "status_value", "status_value-implementations")
    license = "BSL-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "status-value-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::status-value-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "status-value-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "status-value-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["status_valuelite"].names["cmake_find_package"] = "status-value-lite"
        self.cpp_info.components["status_valuelite"].names["cmake_find_package_multi"] = "status-value-lite"
        self.cpp_info.components["status_valuelite"].set_property("cmake_target_name", "nonstd::status-value-lite")
        self.cpp_info.components["status_valuelite"].bindirs = []
        self.cpp_info.components["status_valuelite"].frameworkdirs = []
        self.cpp_info.components["status_valuelite"].libdirs = []
        self.cpp_info.components["status_valuelite"].resdirs = []
