import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class DebugAssert(ConanFile):
    name = "debug_assert"
    description = "Simple, flexible and modular assertion macro"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://foonathan.net/blog/2016/09/16/assertions.html"
    topics = ("assert", "debugging", "utilities", "header-only")

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
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder, keep_path=False)
        copy(self, "debug_assert.hpp",
             dst=os.path.join(self.package_folder, "include"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
