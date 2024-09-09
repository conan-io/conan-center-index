import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class RandomConan(ConanFile):
    name = "effolkronium-random"
    description = "Random for modern C++ with convenient API."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/effolkronium/random"
    topics = ("random", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.MIT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "effolkronium_random")
        self.cpp_info.set_property("cmake_target_name", "effolkronium_random")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "effolkronium_random"
        self.cpp_info.names["cmake_find_package_multi"] = "effolkronium_random"
