import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, replace_in_file
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class RgbcxConan(ConanFile):
    name = "rgbcx"
    description = "High-performance scalar BC1-5 encoders."
    license = ("MIT", "Unlicense")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/richgel999/bc7enc"
    topics = ("BC1", "BC5", "BCx", "encoding", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        replace_in_file(self,
                        os.path.join(self.source_folder, "rgbcx.h"),
                        "#include <stdlib.h>",
                        "#include <stdlib.h>\n#include <string.h>")

    def package(self):
        copy(self, "rgbcx.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "rgbcx_table4.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
