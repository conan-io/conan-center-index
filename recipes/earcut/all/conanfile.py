import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration


class EarcutPackage(ConanFile):
    name = "earcut"
    description = "A C++ port of earcut.js, a fast, header-only polygon triangulation library."
    homepage = "https://github.com/mapbox/earcut.hpp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "ISC"
    topics = ("algorithm", "cpp", "geometry", "rendering", "triangulation",
              "polygon", "header-only", "tessellation", "earcut")
    settings = "compiler"
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
            "Visual Studio": "12"
        }

    @property
    def _minimum_cpp_standard(self):
        return 11

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        else:
            if lazy_lt_semver(str(self.settings.compiler.version), min_version):
                raise ConanInvalidConfiguration(
                    f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*", os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))

    def package_id(self):
        self.info.clear()
