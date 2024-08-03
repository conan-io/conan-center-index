import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class ToonConan(ConanFile):
    name = "toon"
    description = "TooN - Tom's Object Oriented Numerics library"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://codedocs.xyz/edrosten/TooN/"
    topics = ("numerical", "linear-algebra", "matrix", "vector", "optimization", "automatic-differentiation", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["config.hh"]

    options = {
        "with_lapack": [True, False]
    }
    default_options = {
        "with_lapack": True
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "clang": "5",
            "apple-clang": "10",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_lapack:
            self.requires("openblas/0.3.26", options={"build_lapack": True})

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

        if self.options.with_lapack and not self.dependencies["openblas"].options.build_lapack:
            raise ConanInvalidConfiguration(f"{self.ref} requires LAPACK support in OpenBLAS with -o='openblas/*:build_lapack=True'")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             os.path.join(self.source_folder, "TooN"),
             os.path.join(self.package_folder, "include", "TooN"))
        copy(self, "config.hh", self.export_sources_folder,
             os.path.join(self.package_folder, "include", "TooN", "internal"))

        if not self.options.with_lapack:
            replace_in_file(
                self,
                os.path.join(self.package_folder, "include", "TooN", "internal", "config.hh"),
                "define TOON_USE_LAPACK",
                "undef TOON_USE_LAPACK"
        )

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "TooN")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
