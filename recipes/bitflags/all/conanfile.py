import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.50.0"


class BitFlags(ConanFile):
    name = "bitflags"
    description = "Single-header header-only C++11 / C++14 / C++17 library for easily managing set of auto-generated type-safe flags"
    topics = ("bits", "bitflags", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/m-peko/bitflags"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "5",
            "clang": "5",
            "gcc": "7",
            "Visual Studio": "14",
            "msvc": "190",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "bitflags")
        self.cpp_info.set_property("cmake_target_name", "bitflags::bitflags")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
