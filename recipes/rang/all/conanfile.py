from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class RangConan(ConanFile):
    name = "rang"
    description = "A Minimal, Header only Modern c++ library for colors in your terminal"
    homepage = "https://github.com/agauniyal/rang"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Unlicense"
    topics = ("cli", "colors", "terminal", "console")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

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
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "rang")
        self.cpp_info.set_property("cmake_target_name", "rang::rang")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
