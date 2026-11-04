from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.52.0"


class CxxgraphConan(ConanFile):
    name = "cxxgraph"
    description = "Header-Only C++ Library for Graph Representation and Algorithms"
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ZigRazor/CXXGraph/"
    topics = ("graph", "partitioning-algorithms", "dijkstra-algorithm", "graph-theory-algorithms", "header-only")
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
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "17",
            "msvc": "193",
        }

    def configure(self):
        if Version(self.version) < "4.0.0":
            self.license = "AGPL-3.0-later"

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

        # TODO: remove this check once the bug is fixed
        # https://github.com/ZigRazor/CXXGraph/pull/416
        # https://github.com/ZigRazor/CXXGraph/pull/417
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Visual Studio due to fold expression bug")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.h",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread"])
