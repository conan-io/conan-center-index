from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=2.0"


class AarghConan(ConanFile):
    name = "aargh"
    description = "Single-header command-line argument parser for C99 (argh.h)"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ilyabrin/aargh"
    topics = ("cli", "argument-parser", "command-line", "embedded", "header-only")
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
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        # include/aargh: the argh recipe (a C++ library) also ships an argh.h
        copy(self, "argh.h", self.source_folder, os.path.join(self.package_folder, "include", "aargh"))

    def package_info(self):
        self.cpp_info.includedirs = ["include/aargh"]
        self.cpp_info.set_property("cmake_file_name", "aargh")
        self.cpp_info.set_property("cmake_target_name", "aargh::aargh")
        self.cpp_info.set_property("pkg_config_name", "aargh")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
