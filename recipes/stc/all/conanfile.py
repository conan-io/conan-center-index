from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class StcConan(ConanFile):
    name = "stc"
    description = (
        "A modern, user friendly, generic, type-safe and fast C99 container "
        "library: String, Vector, Sorted and Unordered Map and Set, Deque, "
        "Forward List, Smart Pointers, Bitset and Random numbers."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tylov/STC"
    topics = ("containers", "string", "vector", "map", "set", "deque", "bitset", "random", "list")
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
        if self.version == "1.0.0-rc1":
            src_include = self.source_folder
        else:
            src_include = os.path.join(self.source_folder, "include")
        copy(self, "*.h", src=src_include, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
