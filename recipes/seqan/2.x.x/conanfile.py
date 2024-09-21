import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class SeqanConan(ConanFile):
    name = "seqan"
    description = (
        "SeqAn is an open source C++ library of efficient algorithms and data structures for the analysis of sequences "
        "with the focus on biological data. Our library applies a unique generic design that guarantees high performance, "
        "generality, extensibility, and integration with other libraries. "
        "SeqAn is easy to use and simplifies the development of new software tools with a minimal loss of performance."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/seqan/seqan"
    topics = ("algorithms", "data structures", "biological sequences", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "3.4",
            "msvc": "190",
            "Visual Studio": "14",
        }

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning(
                f"{self.name} requires C++{self._min_cppstd}. "
                f"Your compiler is unknown. Assuming it supports C++{self._min_cppstd}."
            )
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++{self._min_cppstd}, which your compiler does not fully support."
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"),
             keep_path=True)
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Windows":
            self.cpp_info.defines = ["NOMINMAX"]
