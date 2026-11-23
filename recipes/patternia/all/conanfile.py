import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class PatterniaConan(ConanFile):
    name = "patternia"
    description = "Header-only pattern matching library for modern C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sentomk/patternia"
    topics = ("pattern-matching", "match", "variant", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        # Mirrors upstream cmake/CheckCompilerVersion.cmake.
        return {
            "gcc": "11",
            "clang": "12",
            "apple-clang": "14",
            "msvc": "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        compiler = str(self.settings.compiler)
        minimum_version = self._compilers_minimum_version.get(compiler)
        if compiler == "clang" and self.settings.os == "Windows":
            # clang-cl and clang with the MSVC toolchain need Clang 18.
            minimum_version = "18"
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {self.settings.compiler} "
                f">= {minimum_version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "patternia")
        self.cpp_info.set_property("cmake_target_name", "patternia::patternia")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
