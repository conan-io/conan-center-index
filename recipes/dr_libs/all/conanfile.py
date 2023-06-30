from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

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

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "4.7",
            "clang": "3.4",
            "apple-clang": "6",
        }

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 180)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(
                str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
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
