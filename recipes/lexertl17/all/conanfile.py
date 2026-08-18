from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=2.0.9"

class Lexertl17Conan(ConanFile):
    name = "lexertl17"
    description = "The Modular Lexical Analyser Generator"
    license = "BSL-1.0 AND Unicode-3.0"
    homepage = "https://github.com/BenHanson/lexertl17"
    url = "https://github.com/conan-io/conan-center-index"

    topics = (
        "lexer",
        "lexical-analyser",
        "lexical-analyzer",
        "parser",
        "header-only",
    )

    package_type = "header-library"

    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self)

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
        )

    def package(self):
        copy(
            self,
            "include/*",
            src=self.source_folder,
            dst=self.package_folder,
        )

        copy(
            self,
            "LICENSE*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

        copy(
            self,
            "*license*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
            ignore_case=True,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "lexertl17")
        self.cpp_info.set_property("cmake_target_name", "lexertl17::lexertl17")

    def package_id(self):
        self.info.clear()
