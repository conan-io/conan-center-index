import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


required_conan_version = ">=1.52.0"


class PolyLiteConan(ConanFile):
    name = "polylite"
    description = (
        "Header-only C++23 multiprotocol library for CBOR, JSON, TOML and YAML."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kristianivarsson/polylite"
    topics = ("json", "yaml", "toml", "cbor", "header-only", "cpp23", "parser")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, 23)

    def package_id(self):
        self.info.clear()

    def package(self):
        copy(
            self,
            "*.hpp",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "polylite")
        self.cpp_info.set_property("cmake_target_name", "polylite::polylite")
