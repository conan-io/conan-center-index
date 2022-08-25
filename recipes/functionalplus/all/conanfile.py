from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class FunctionalPlusConan(ConanFile):
    name = "functionalplus"
    description = "Functional Programming Library for C++."
    license = "BSL-1.0"
    topics = ("functionalplus", "fplus", "functional programming")
    homepage = "https://github.com/Dobiasd/FunctionalPlus"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "4.9",
            "Visual Studio": "14",
            "msvc": "190",
            "clang": "3.7",
            "apple-clang": "9",
        }

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("functionalplus requires C++14, which your compiler does not support.")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "FunctionalPlus")
        self.cpp_info.set_property("cmake_target_name", "FunctionalPlus::fplus")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["fplus"].bindirs = []
        self.cpp_info.components["fplus"].frameworkdirs = []
        self.cpp_info.components["fplus"].libdirs = []
        self.cpp_info.components["fplus"].resdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["fplus"].system_libs = ["pthread"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "FunctionalPlus"
        self.cpp_info.names["cmake_find_package_multi"] = "FunctionalPlus"
        self.cpp_info.components["fplus"].names["cmake_find_package"] = "fplus"
        self.cpp_info.components["fplus"].names["cmake_find_package_multi"] = "fplus"
        self.cpp_info.components["fplus"].set_property("cmake_target_name", "FunctionalPlus::fplus")
