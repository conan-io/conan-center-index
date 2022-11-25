from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout

import os

required_conan_version = ">=1.50.0"

class ItlibConan(ConanFile):
    name = "itlib"
    description = "A collection of small single-header C++ libraries similar to or extending the C++ standard library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/iboB/itlib"
    topics = ("template", "flatmatp", "static-vector")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, pattern="*.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
