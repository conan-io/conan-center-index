from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class WuffsConan(ConanFile):
    name = "wuffs"
    description = "Wrangling Untrusted File Formats Safely (Wuffs) is a memory-safe library for parsing/decoding/encoding images, audio, video, fonts and compressed archives."
    license = "Apache-2.0 OR MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/wuffs"
    topics = ("wuffs", "image", "parser", "decoder", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "wuffs-*.c",
            src=os.path.join(self.source_folder, "release", "c"),
            dst=os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            "wuffs-*.c",
            src=os.path.join(self.source_folder, "release", "c"),
            dst=os.path.join(self.package_folder, "include", "wuffs"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "wuffs")
        self.cpp_info.set_property("cmake_target_name", "wuffs::wuffs")

