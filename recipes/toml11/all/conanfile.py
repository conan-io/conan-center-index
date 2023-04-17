from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class Toml11Conan(ConanFile):
    name = "toml11"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ToruNiina/toml11"
    description = "TOML for Modern C++"
    topics = ("toml", "c-plus-plus-11", "c-plus-plus", "parser", "serializer")
    license = "MIT"
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
        copy(self, "toml.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "toml11"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "toml"), dst=os.path.join(self.package_folder, "include", "toml11", "toml"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "toml11")
        self.cpp_info.set_property("cmake_target_name", "toml11::toml11")
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs.append(os.path.join("include", "toml11"))
        self.cpp_info.libdirs = []
