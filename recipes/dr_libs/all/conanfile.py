from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class DrLibsConan(ConanFile):
    name = "dr_libs"
    description = "Public domain, single file audio decoding libraries for C and C++."
    license = ("Unlicense", "MIT-0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mackron/dr_libs"
    topics = ("audio", "encoding", "header-only")
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
            excludes=("old/*", "wip/*", "tests/*")
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
