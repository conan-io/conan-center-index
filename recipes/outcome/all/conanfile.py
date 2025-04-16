import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class OutcomeConan(ConanFile):
    name = "outcome"
    description = "Provides very lightweight outcome<T> and result<T>"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/outcome"
    topics = ("result", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = { "single_header": [True, False] }
    default_options = { "single_header": True }

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "clang": "3.9",
            "gcc": "6",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if not self.options.single_header:
            self.requires("quickcpplib/cci.20231208")
            self.requires("status-code/cci.20240614")

    def package_id(self):
        self.info.settings.clear()

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
        copy(self, "Licence.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.options.single_header:
            copy(self, "outcome.hpp", src=os.path.join(self.source_folder, "single-header"),
                                      dst=os.path.join(self.package_folder, "include"))
        else:
            copy(self, "*", src=os.path.join(self.source_folder, "include"),
                            dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
