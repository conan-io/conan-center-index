import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class GraphthewyConan(ConanFile):
    name = "graphthewy"
    description = "Simple header-only C++ Library for graph modelling (directed or not) and graph cycle detection. "
    license = "EUPL-1.2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alex-87/graphthewy"
    topics = ("graph", "algorithm", "modelling", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "msvc": "191",
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10"
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
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.hpp", dst=os.path.join(self.package_folder, "include", "graphthewy"), src=self.source_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
