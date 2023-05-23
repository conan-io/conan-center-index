from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class TlfunctionrefConan(ConanFile):
    name = "tl-function-ref"
    description = "A lightweight, non-owning reference to a callable."
    license = "CC0-1.0"
    topics = ("function_ref", "callable")
    homepage = "https://github.com/TartanLlama/function_ref"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

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
        self.cpp_info.set_property("cmake_file_name", "tl-function-ref")
        self.cpp_info.set_property("cmake_target_name", "tl::function-ref")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "tl-function-ref"
        self.cpp_info.filenames["cmake_find_package_multi"] = "tl-function-ref"
        self.cpp_info.names["cmake_find_package"] = "tl"
        self.cpp_info.names["cmake_find_package_multi"] = "tl"
        self.cpp_info.components["function-ref"].names["cmake_find_package"] = "function-ref"
        self.cpp_info.components["function-ref"].names["cmake_find_package_multi"] = "function-ref"
        self.cpp_info.components["function-ref"].set_property("cmake_target_name", "tl::function-ref")
        self.cpp_info.components["function-ref"].bindirs = []
        self.cpp_info.components["function-ref"].frameworkdirs = []
        self.cpp_info.components["function-ref"].libdirs = []
        self.cpp_info.components["function-ref"].resdirs = []
