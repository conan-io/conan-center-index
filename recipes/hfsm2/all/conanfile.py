import os

from conan import ConanFile
from conan.tools.files import copy
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.files import get

required_conan_version = ">=2.0"

class Hfsm2Conan(ConanFile):
    name = "hfsm2"
    description = "High-Performance Hierarchical Finite State Machine Framework"
    license = "MIT"
    topics = ("embedded", "fsm", "state-machine", "cpp", "modern-cpp", "game-development",
              "cpp11", "embedded-systems", "template-metaprogramming", "header-only",
              "mit-license", "fsm-library", "hierarchical-state-machine", "game-dev", "hfsm")
    homepage = "https://hfsm.dev/"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
