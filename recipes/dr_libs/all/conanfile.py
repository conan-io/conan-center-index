from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, load, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

class DrLibsConan(ConanFile):
    name = "dr_libs"
    description = "Public domain, single file audio decoding libraries for C and C++."
    license = ("Public Domain", "MIT No Attribution")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mackron/dr_libs"
    topics = ("audio", "encoding", "header-only")
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

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