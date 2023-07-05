from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


import os


class NanoRTConan(ConanFile):
    name = "nanort"
    description = "Single header only modern ray tracing kernel"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lighttransport/nanort"
    topics = ("graphics", "raytracing", "header-only")
    license = "MIT"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
       get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "nanort.h", self.source_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
