from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class TaoCPPSequencesonan(ConanFile):
    name = "taocpp-sequences"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/taocpp/sequences"
    description = "Variadic templates and std::integer_sequence support library"
    topics = ("variadic-template", "template", "interger-sequence")
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

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
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "taocpp-sequences")
        self.cpp_info.set_property("cmake_target_name", "taocpp::sequences")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "taocpp-sequences"
        self.cpp_info.filenames["cmake_find_package_multi"] = "taocpp-sequences"
        self.cpp_info.names["cmake_find_package"] = "taocpp"
        self.cpp_info.names["cmake_find_package_multi"] = "taocpp"
        self.cpp_info.components["_taocpp-sequences"].names["cmake_find_package"] = "sequences"
        self.cpp_info.components["_taocpp-sequences"].names["cmake_find_package_multi"] = "sequences"
        self.cpp_info.components["_taocpp-sequences"].set_property("cmake_target_name", "taocpp::sequences")
        self.cpp_info.components["_taocpp-sequences"].bindirs = []
        self.cpp_info.components["_taocpp-sequences"].libdirs = []
