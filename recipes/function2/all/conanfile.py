from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class Function2Conan(ConanFile):
    name = "function2"
    description = "Improved and configurable drop-in replacement to std::function that supports move only types, multiple overloads and more"
    topics = ("function", "functional", "function-wrapper", "type-erasure", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Naios/function2"
    license = "BSL-1.0"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compiler_minimal_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "14",
            "msvc": "14",
        }

    def layout(self):
        basic_layout(self)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
