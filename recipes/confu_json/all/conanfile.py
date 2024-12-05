from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class ConfuJson(ConanFile):
    name = "confu_json"
    homepage = "https://github.com/werto87/confu_json"
    description = "Uses boost::fusion to help with serialization; json <-> user defined type"
    topics = ("json", "serialization", "user-defined-type", "header-only")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "17",
            "msvc": "193",
            "gcc": "10",
            "clang": "10",
            "apple-clang": "13",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.85.0")
        self.requires("magic_enum/0.9.6")

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
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h*", os.path.join(self.source_folder, "confu_json"),
                           os.path.join(self.package_folder, "include", "confu_json"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.requires = ["boost::headers", "magic_enum::magic_enum"]
