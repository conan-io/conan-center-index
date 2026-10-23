import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0.9"


class StellarConan(ConanFile):
    name = "stellar"
    description = (
        "Header-only C++23 toolkit extensions (ste::) — string, collection, "
        "async and StringBuilder utilities."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stescobedo92/stellar"
    topics = ("cpp23", "cxx23", "string", "utilities", "header-only",
              "coroutines", "ranges")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 23

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc":            "13",
            "clang":          "17",
            "apple-clang":    "15",
            "Visual Studio":  "17",
            "msvc":           "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}. "
                f"{self.settings.compiler} {self.settings.compiler.version} is not supported."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name",   "stellar")
        self.cpp_info.set_property("cmake_target_name", "stellar::stellar")
        self.cpp_info.set_property("pkg_config_name",   "stellar")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
