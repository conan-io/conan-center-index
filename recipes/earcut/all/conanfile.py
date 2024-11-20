import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.50.0"


class EarcutPackage(ConanFile):
    name = "earcut"
    description = "A C++ port of earcut.js, a fast, header-only polygon triangulation library."
    homepage = "https://github.com/mapbox/earcut.hpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "ISC"
    topics = ("algorithm", "cpp", "geometry", "rendering", "triangulation",
              "polygon", "header-only", "tessellation")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_compilers_version(self):
        # References:
        # * https://github.com/mapbox/earcut.hpp#dependencies
        # * https://en.cppreference.com/w/cpp/compiler_support/11
        # * https://en.wikipedia.org/wiki/Xcode#Toolchain_versions
        return {
            "apple-clang": "5.1",
            "clang": "3.4",
            "gcc": "4.9",
            "intel": "15",
            "sun-cc": "5.14",
            "Visual Studio": "12",
            "msvc": "180",
        }

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

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and loose_lt_semver(str(self.settings.compiler.version), min_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*", os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "earcut_hpp")
        self.cpp_info.set_property("cmake_target_name", "earcut_hpp::earcut_hpp")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "earcut_hpp"
        self.cpp_info.names["cmake_find_package_multi"] = "earcut_hpp"
