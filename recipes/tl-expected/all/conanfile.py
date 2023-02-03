from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class TlExpectedConan(ConanFile):
    name = "tl-expected"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://tl.tartanllama.xyz"
    description = "C++11/14/17 std::expected with functional-style extensions"
    topics = ("cpp11", "cpp14", "cpp17", "expected")
    license = "CC0-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tl-expected")
        self.cpp_info.set_property("cmake_target_name", "tl::expected")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tl-expected"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tl-expected"
        self.cpp_info.names["cmake_find_package"] = "tl"
        self.cpp_info.names["cmake_find_package_multi"] = "tl"
        self.cpp_info.components["expected"].names["cmake_find_package"] = "expected"
        self.cpp_info.components["expected"].names["cmake_find_package_multi"] = "expected"
        self.cpp_info.components["expected"].set_property("cmake_target_name", "tl::expected")
        self.cpp_info.components["expected"].bindirs = []
        self.cpp_info.components["expected"].frameworkdirs = []
        self.cpp_info.components["expected"].libdirs = []
        self.cpp_info.components["expected"].resdirs = []
