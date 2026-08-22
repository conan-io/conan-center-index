import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class CTPGConan(ConanFile):
    name = "ctpg"
    description = (
        "Compile Time Parser Generator is a C++ single header library which takes a language description as a C++ code "
        "and turns it into a LR1 table parser with a deterministic finite automaton lexical analyzer, all in compile time."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/peter-winter/ctpg"
    topics = ("regex", "parser", "grammar", "compile-time", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "12",
            "apple-clang": "12.0",
            "msvc": "192",
            "Visual Studio": "16",
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
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE*",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        include_dir = os.path.join("include", "ctpg")
        copy(self, "ctpg.hpp",
             dst=os.path.join(self.package_folder, include_dir),
             src=os.path.join(self.source_folder, include_dir))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
