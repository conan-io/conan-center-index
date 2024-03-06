from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=1.50.0"

class WyhashConan(ConanFile):
    name = "wyhash"
    description = "The FASTEST QUALITY hash function, random number generators (PRNG) and hash map."
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wangyi-fudan/wyhash"
    topics = ("bloom-filter", "hash", "random-number-generators", "header-only")
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
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
