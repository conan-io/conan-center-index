from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class PerlinnoiseConan(ConanFile):
    name = "perlinnoise"
    description = "Header-only Perlin noise library for modern C++ "
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Reputeless/PerlinNoise/"
    topics = ("noise", "perlin", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compiler_required_cpp(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compiler_required_cpp.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        else:
            self.output.warn(f"{self.ref} requires C++{self._min_cppstd}. Your compiler is unknown. Assuming it supports C++{self._min_cppstd}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "PerlinNoise")
        self.cpp_info.set_property("cmake_target_name", "siv::PerlinNoise")

        self.cpp_info.components["siv"].set_property("cmake_target_name", "siv::PerlinNoise")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PerlinNoise"
        self.cpp_info.filenames["cmake_find_package_multi"] = "PerlinNoise"
        self.cpp_info.names["cmake_find_package"] = "siv"
        self.cpp_info.names["cmake_find_package_multi"] = "siv"

        self.cpp_info.components["siv"].names["cmake_find_package"] = "PerlinNoise"
        self.cpp_info.components["siv"].names["cmake_find_package_multi"] = "PerlinNoise"
