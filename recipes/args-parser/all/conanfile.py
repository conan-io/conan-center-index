from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class ArgsParserConan(ConanFile):
    name = "args-parser"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/args-parser"
    license = "MIT"
    description = "Small C++ header-only library for parsing command line arguments."
    topics = ("argument", "parsing")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "10",
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
                f"{self.name} {self.version} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "args-parser"), dst=os.path.join(self.package_folder, "include", "args-parser"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "args-parser")
        self.cpp_info.set_property("cmake_target_name", "args-parser::args-parser")
        self.cpp_info.includedirs.append(os.path.join("include", "args-parser"))
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
