from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class ByteLiteConan(ConanFile):
    name = "byte-lite"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinmoene/byte-lite"
    description = ("byte lite - A single-file header-only C++17-like byte type for \
                    C++98, C++11 and later")
    topics = ("cpp11", "cpp14", "cpp17", "byte", "byte-implementations")
    license = "BSL-1.0"
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
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "byte-lite")
        self.cpp_info.set_property("cmake_target_name", "nonstd::byte-lite")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
