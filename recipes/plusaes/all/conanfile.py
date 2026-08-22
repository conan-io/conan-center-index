import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class PlusaesConan(ConanFile):
    name = "plusaes"
    description = "Header only C++ AES cipher library"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kkAyataka/plusaes"
    topics = ("encryption", "header-only")

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
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        root_dir = self.source_folder
        include_dir = os.path.join(root_dir, "include")
        copy(self, "LICENSE_1_0.txt", dst=os.path.join(self.package_folder, "licenses"), src=root_dir)
        copy(self, "*plusaes.hpp", dst=os.path.join(self.package_folder, "include"), src=include_dir)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
