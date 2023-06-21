from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class TaoCPPPEGTLConan(ConanFile):
    name = "taocpp-pegtl"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/pegtl"
    description = "Parsing Expression Grammar Template Library"
    topics = ("peg", "header-only", "cpp",
              "parsing", "cpp17", "cpp11", "grammar")
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pegtl")
        self.cpp_info.set_property("cmake_target_name", "taocpp::pegtl")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "pegtl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "pegtl"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-pegtl"].names["cmake_find_package"] = "pegtl"
        self.cpp_info.components["_taocpp-pegtl"].names["cmake_find_package_multi"] = "pegtl"
        self.cpp_info.components["_taocpp-pegtl"].set_property("cmake_target_name", "taocpp::pegtl")
