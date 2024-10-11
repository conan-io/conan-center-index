from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class BackportCppRecipe(ConanFile):
    name = "backport-cpp"
    description = "An ongoing effort to bring modern C++ utilities to be compatible with C++11"
    topics = ("header-only", "backport")
    homepage = "https://github.com/bitwizeshift/BackportCpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source=True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, os.path.join("include", "**", "*.hpp"), src=self.source_folder, dst=self.package_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Backport")
        self.cpp_info.set_property("cmake_target_name", "Backport::Backport")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Backport"
        self.cpp_info.names["cmake_find_package_multi"] = "Backport"
