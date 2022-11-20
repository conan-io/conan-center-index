from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import os

required_conan_version = ">=1.52.0"

class CpplazyConan(ConanFile):
    name = "cpp-lazy"
    description = "C++11/14/17/20 library for lazy evaluation "
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/MarcDirven/cpp-lazy"
    topics = ("lazy evaluation", "header-only")
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

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "6.0":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support gcc < 6.0.")
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "12.0":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support apple-clang < 12.0.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
