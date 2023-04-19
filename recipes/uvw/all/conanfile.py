from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os
import re


required_conan_version = ">=1.54.0"


class UvwConan(ConanFile):
    name = "uvw"
    description = "Header-only, event based, tiny and easy to use libuv wrapper in modern C++."
    topics = ("uvw", "libuv", "io", "networking", "header-only",)
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skypjack/uvw"
    package_type = "header-library"
    no_copy_source = True
    settings = "compiler"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    @property
    def _required_libuv_version(self):
        # uvw is bound to a particular libuv version which is part of the release archive name
        match = re.match(r".*libuv[_-]v([0-9]+\.[0-9]+).*", self.conan_data["sources"][self.version]["url"])
        if not match:
            raise ConanException(f"{self.ref} does not know what version of libuv to use as a dependency")
        return match.group(1)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"libuv/[~{self._required_libuv_version}]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{self.ref} requires C++{self._min_cppstd}, which your compiler doesn't support")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*", src=os.path.join(self.source_folder, "src", "uvw"), dst=os.path.join(self.package_folder, "include", "uvw"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
