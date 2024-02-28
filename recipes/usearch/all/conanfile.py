import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout


required_conan_version = ">=1.53.0"


class USearchConan(ConanFile):
    name = "usearch"
    license = "Apache-2.0"
    description = "Smaller & Faster Single-File Vector Search Engine from Unum"
    homepage = "https://unum-cloud.github.io/usearch/"
    topics = ("search", "vector", "simd", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("fp16/cci.20210320")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "usearch")
        self.cpp_info.set_property("cmake_target_name", "usearch::usearch")
        self.cpp_info.set_property("pkg_config_name", "usearch")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
