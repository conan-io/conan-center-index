from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class FunctionalPlusConan(ConanFile):
    name = "functionalplus"
    description = "Functional Programming Library for C++."
    license = "BSL-1.0"
    topics = ("fplus", "functional programming", "header-only")
    homepage = "https://github.com/Dobiasd/FunctionalPlus"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "4.9",
            "Visual Studio": "14",
            "msvc": "190",
            "clang": "3.7",
            "apple-clang": "9",
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
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
            src=os.path.join(self.source_folder, "include"),
            dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "FunctionalPlus")
        self.cpp_info.set_property("cmake_target_name", "FunctionalPlus::fplus")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["fplus"].system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "FunctionalPlus"
        self.cpp_info.names["cmake_find_package_multi"] = "FunctionalPlus"
        self.cpp_info.components["fplus"].names["cmake_find_package"] = "fplus"
        self.cpp_info.components["fplus"].names["cmake_find_package_multi"] = "fplus"
        self.cpp_info.components["fplus"].set_property("cmake_target_name", "FunctionalPlus::fplus")
        self.cpp_info.components["fplus"].bindirs = []
        self.cpp_info.components["fplus"].frameworkdirs = []
        self.cpp_info.components["fplus"].libdirs = []
        self.cpp_info.components["fplus"].resdirs = []
