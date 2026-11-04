import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class So5extraConan(ConanFile):
    name = "so5extra"
    description = "A collection of various SObjectizer's extensions."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Stiffstream/so5extra"
    topics = ("concurrency", "actor-framework", "actors", "agents", "sobjectizer", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        if self.version >= Version("1.6.0"):
            # Since v1.6.0 requirements to compilers were updated:
            return {
                "gcc": "10",
                "clang": "11",
                "apple-clang": "13",
                "Visual Studio": "17",
                "msvc": "192"
            }
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191"
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.version >= Version("1.6.0"):
            self.requires("sobjectizer/5.8.1")
        else:
            self.requires("sobjectizer/5.7.4")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        compiler = str(self.settings.compiler)
        if compiler not in self._compilers_minimum_version:
            self.output.warning(f"{self.name} recipe lacks information about the {compiler} compiler standard version support")
            self.output.warning(f"{self.name} requires a compiler that supports at least C++{self._min_cppstd}")
            return
        version = Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(f"{self.name} requires a compiler that supports at least C++{self._min_cppstd}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp",
             dst=os.path.join(self.package_folder, "include/so_5_extra"),
             src=os.path.join(self.source_folder, "dev", "so_5_extra"))
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "so5extra")
        self.cpp_info.set_property("cmake_target_name", "sobjectizer::so5extra")
        self.cpp_info.components["so_5_extra"].set_property("cmake_target_name", "sobjectizer::so5extra")
        self.cpp_info.components["so_5_extra"].requires = ["sobjectizer::sobjectizer"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "so5extra"
        self.cpp_info.filenames["cmake_find_package_multi"] = "so5extra"
        self.cpp_info.names["cmake_find_package"] = "sobjectizer"
        self.cpp_info.names["cmake_find_package_multi"] = "sobjectizer"
        self.cpp_info.components["so_5_extra"].names["cmake_find_package"] = "so5extra"
        self.cpp_info.components["so_5_extra"].names["cmake_find_package_multi"] = "so5extra"
