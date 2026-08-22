import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class KainjowMustacheConan(ConanFile):
    name = "kainjow-mustache"
    description = "Mustache text templates for modern C++"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kainjow/Mustache"
    topics = ("mustache", "template", "header-only")

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
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "mustache.hpp",
             dst=os.path.join(self.package_folder, "include", "kainjow"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "kainjow_mustache")
        self.cpp_info.set_property("cmake_target_name", "kainjow_mustache::kainjow_mustache")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "kainjow_mustache"
        self.cpp_info.names["cmake_find_package_multi"] = "kainjow_mustache"
