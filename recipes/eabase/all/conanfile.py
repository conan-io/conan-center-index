import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class EABaseConan(ConanFile):
    name = "eabase"
    description = "EABase is a small set of header files that define platform-independent data types and platform feature macros. "
    topics = ("eastl", "config")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/electronicarts/EABase"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs += [
            os.path.join("include", "Common"),
            os.path.join("include", "Common", "EABase"),
        ]

        self.cpp_info.set_property("cmake_file_name", "EABase")
        self.cpp_info.set_property("cmake_target_name", "EABase::EABase")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "EABase"
        self.cpp_info.filenames["cmake_find_package_multi"] = "EABase"
        self.cpp_info.names["cmake_find_package"] = "EABase"
        self.cpp_info.names["cmake_find_package_multi"] = "EABase"
