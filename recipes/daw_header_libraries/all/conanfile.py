from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import os

required_conan_version = ">=1.50.0"


class DawHeaderLibrariesConan(ConanFile):
    name = "daw_header_libraries"
    description = "Various header libraries mostly future std lib, replacements for(e.g. visit), or some misc"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/beached/header_libraries"
    topics = ("algorithms", "helpers", "data-structures")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.get_safe("compiler.version")) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "daw-header-libraries")
        self.cpp_info.set_property("cmake_target_name", "daw::daw-header-libraries")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "daw-header-libraries"
        self.cpp_info.filenames["cmake_find_package_multi"] = "daw-header-libraries"
        self.cpp_info.names["cmake_find_package"] = "daw"
        self.cpp_info.names["cmake_find_package_multi"] = "daw"
        self.cpp_info.components["daw"].names["cmake_find_package"] = "daw-header-libraries"
        self.cpp_info.components["daw"].names["cmake_find_package_multi"] = "daw-header-libraries"
        self.cpp_info.components["daw"].set_property("cmake_target_name", "daw::daw-header-libraries")
