from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "flux"
    description = ("Flux is an experimental C++20 library for working with sequences of values. "
                   "It offers similar facilities to C++20 ranges, D ranges, Python itertools, "
                   "Rust iterators and related libraries for other languages.")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tcbrindle/flux"
    topics = ("algorithms", "collections", "sequences", "ranges", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        # https://github.com/tcbrindle/flux/blob/e942a678/CMakeLists.txt#L21
        if is_msvc(self):
            return 23
        return 20

    @property
    def _compilers_minimum_version(self):
        # https://github.com/tcbrindle/flux?tab=readme-ov-file#compiler-support
        return {
            "apple-clang": "15",
            "clang": "16",
            "gcc": "11",
            "msvc": "193",
            "Visual Studio": "17",
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

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE_1_0.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "flux")
        self.cpp_info.set_property("cmake_target_name", "flux::flux")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

