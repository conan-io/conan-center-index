from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

class CppYyjsonConan(ConanFile):
    name = "cpp-yyjson"
    description = "Ultra-fast and intuitive C++ JSON reader/writer with yyjson backend"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yosh-matsuda/cpp-yyjson"
    topics = ("json", "reader", "writer", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "15",
            "apple-clang": "14",
            "Visual Studio": "17",
            "msvc": "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "0.6.0":
            self.requires("yyjson/0.9.0")
        else:
            self.requires("yyjson/0.10.0")
        self.requires("fmt/10.2.1")
        self.requires("nameof/0.10.4")

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
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if is_msvc(self):
            self.cpp_info.cxxflags.append("/Zc:preprocessor")

        self.cpp_info.set_property("cmake_file_name", "cpp_yyjson")
        self.cpp_info.set_property("cmake_target_name", "cpp_yyjson::cpp_yyjson")
