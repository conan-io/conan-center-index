from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class Toml11Conan(ConanFile):
    name = "toml11"
    description = "TOML for Modern C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ToruNiina/toml11"
    topics = ("toml", "c-plus-plus-11", "c-plus-plus", "parser", "serializer", "header-only")
    package_type = "header-library"
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
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        if Version(self.version) < "4.0.0":
            copy(self, "toml.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "toml11"))
            copy(self, "*.hpp", src=os.path.join(self.source_folder, "toml"), dst=os.path.join(self.package_folder, "include", "toml11", "toml"))
        else:
            copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "toml11")
        self.cpp_info.set_property("cmake_target_name", "toml11::toml11")

        self.cpp_info.includedirs.append(os.path.join("include", "toml11"))
