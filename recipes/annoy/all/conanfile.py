import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"

class AnnoyConan(ConanFile):
    name = "annoy"
    description = "Approximate Nearest Neighbors optimized for memory usage and loading/saving to disk"
    license = "Apache-2.0"
    homepage = "https://github.com/spotify/annoy"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("approximate-nearest-neighbors", "machine-learning", "nearest-neighbors", "header-only")

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
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        for header in ["annoylib.h", "kissrandom.h", "mman.h"]:
            copy(self, header, os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "include", "annoy"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Annoy")
        self.cpp_info.set_property("cmake_target_name", "Annoy::Annoy")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Annoy"
        self.cpp_info.names["cmake_find_package_multi"] = "Annoy"
