from conan import ConanFile
from conan.tools import files
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.51.3"


class JfalcouEveConan(ConanFile):
    name = "jfalcou-eve"
    description = ("Expressive Velocity Engine - reimplementation of the old "
                   "Boost.SIMD on C++20"
                   )
    homepage = "https://jfalcou.github.io/eve/"
    topics = ("cpp", "simd")
    license = ("MIT", "BSL-1.0")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True


    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {"gcc": "11",
                "Visual Studio": "16.9",
                "msvc": "1928",
                "clang": "13",
                "apple-clang": "13"}

    def configure(self):
        version = Version(self.version.strip("v"))
        if version.major < 2022 or (version.major == 2022 and version.minor < 9):
            self.license = "MIT"
        else:
            self.license = "BSL-1.0"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        # FIXME: Need to use self.info.settings for header-only
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if is_msvc(self):
            raise ConanInvalidConfiguration("EVE does not support MSVC yet (https://github.com/jfalcou/eve/issues/1022).")
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("EVE does not support apple Clang due to an incomplete libcpp.")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(f"{self.ref} requires C++{self._min_cppstd}. Your compiler is unknown. Assuming it supports C++{self._min_cppstd}.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def package_id(self):
        self.info.clear()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def package(self):
        copy(self, pattern="*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "eve"
        self.cpp_info.names["cmake_find_package_multi"] = "eve"
        self.cpp_info.set_property("cmake_file_name", "eve")
        self.cpp_info.set_property("cmake_target_name", "eve::eve")
