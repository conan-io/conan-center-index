from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.50.0"


class JfalcouEveConan(ConanFile):
    name = "jfalcou-eve"
    description = ("Expressive Velocity Engine - reimplementation of the old "
                   "Boost.SIMD on C++20"
                   )
    license = ("MIT", "BSL-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://jfalcou.github.io/eve/"
    topics = ("cpp", "simd", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "Visual Studio": "16.9",
            "msvc": "192",
            "clang": "13",
            "apple-clang": "14",
        }

    def configure(self):
        if Version(self.version.strip("v")) < "2022.09.0":
            self.license = "MIT"
        else:
            self.license = "BSL-1.0"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if is_msvc(self) and Version(self.version.strip("v")) < "2023.02.15":
            raise ConanInvalidConfiguration(f"{self.ref} does not support MSVC. See https://github.com/jfalcou/eve/issues/1022")

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "eve")
        self.cpp_info.set_property("cmake_target_name", "eve::eve")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "eve"
        self.cpp_info.names["cmake_find_package_multi"] = "eve"
