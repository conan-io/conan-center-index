from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class JthreadLiteConan(ConanFile):
    name = "jthread-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/jthread-lite"
    description = "jthread lite - C++20's jthread for C++11 and later in a single-file header-only library "
    topics = ("jthread-lite", "jthread", "cpp11")
    license = "BSL-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jthread-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::jthread-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # TODO: back to global scope once cmake_find_package* generators removed
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["jthreadlite"].system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "jthread-lite"
        self.cpp_info.filenames["cmake_find_package_multi"] = "jthread-lite"
        self.cpp_info.names["cmake_find_package"] = "nonstd"
        self.cpp_info.names["cmake_find_package_multi"] = "nonstd"
        self.cpp_info.components["jthreadlite"].names["cmake_find_package"] = "jthread-lite"
        self.cpp_info.components["jthreadlite"].names["cmake_find_package_multi"] = "jthread-lite"
        self.cpp_info.components["jthreadlite"].set_property("cmake_target_name", "nonstd::jthread-lite")
        self.cpp_info.components["jthreadlite"].bindirs = []
        self.cpp_info.components["jthreadlite"].libdirs = []
