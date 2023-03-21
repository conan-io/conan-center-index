from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

class MDSpanConan(ConanFile):
    name = "mdspan"
    description = "Production-quality reference implementation of mdspan"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kokkos/mdspan"
    topics = ("multi-dimensional", "array", "span", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15" if Version(self.version) < "0.2.0" else "16",
            "msvc": "191" if Version(self.version) < "0.2.0" else "192",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1"
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn(f"{self.ref} recipe lacks information about the {self.settings.compiler} "
                             "compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._minimum_cpp_standard} support. "
                    "The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it.")

        if str(self.settings.compiler) == "Visual Studio" and "16.6" <= Version(self.settings.compiler.version) < "17.0":
            raise ConanInvalidConfiguration(
                "Unsupported Visual Studio version due to upstream bug. The supported Visual Studio versions are (< 16.6 or 17.0 <=)."
                "See upstream issue https://github.com/kokkos/mdspan/issues/26 for details.")
        # TODO: check msvcc version more precisely
        if self.settings.compiler == "msvc" and Version(self.settings.compiler.version) == "192":
            raise ConanInvalidConfiguration(
                "Unsupported MSVC version due to upstream bug. The supported MSVC versions are (< 192 or 193 <=)."
                "See upstream issue https://github.com/kokkos/mdspan/issues/26 for details.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="*LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "mdspan")
        self.cpp_info.set_property("cmake_target_name", "std::mdspan")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "mdspan"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mdspan"
        self.cpp_info.names["cmake_find_package"] = "std"
        self.cpp_info.names["cmake_find_package_multi"] = "std"
        self.cpp_info.components["_mdspan"].names["cmake_find_package"] = "mdspan"
        self.cpp_info.components["_mdspan"].names["cmake_find_package_multi"] = "mdspan"
