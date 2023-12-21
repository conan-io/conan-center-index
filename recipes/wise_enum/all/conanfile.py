from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class WiseEnumConan(ConanFile):
    name = "wise_enum"
    description = (
        "Header-only C++11/14/17 library provides static reflection for enums, "
        "work with any enum type without any boilerplate code."
    )
    topics = (
        "cplusplus",
        "enum-to-string",
        "string-to-enum"
        "serialization",
        "reflection",
        "header-only",
        "compile-time"
    )
    homepage = "https://github.com/quicknir/wise_enum"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSL-1.0"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio is not supported")

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
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "WiseEnum")
        self.cpp_info.set_property("cmake_target_name", "WiseEnum::wise_enum")
        self.cpp_info.set_property("pkg_config_name", "WiseEnum")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "WiseEnum"
        self.cpp_info.names["cmake_find_package_multi"] = "WiseEnum"
        self.cpp_info.names["pkg_config"] = "WiseEnum"
        self.cpp_info.components["_wise_enum"].names["cmake_find_package"] = "wise_enum"
        self.cpp_info.components["_wise_enum"].names["cmake_find_package_multi"] = "wise_enum"
        self.cpp_info.components["_wise_enum"].set_property("cmake_target_name", "WiseEnum::wise_enum")
        self.cpp_info.components["_wise_enum"].set_property("pkg_config_name", "WiseEnum")
        self.cpp_info.components["_wise_enum"].bindirs = []
        self.cpp_info.components["_wise_enum"].libdirs = []
