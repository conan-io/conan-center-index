import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2.1"


class QcHashConan(ConanFile):
    name = "qc-hash"
    license = "MIT"
    homepage = "https://github.com/Daskie/qc-hash"
    url = "https://github.com/Daskie/qc-hash"
    description = "QC Hash - Extremely fast unordered map and set library for C++20"
    topics = (
        "geometry",
        "mesh-processing",
        "polygon-mesh",
        "hash-table",
        "unordered-map",
        "unordered-set",
    )
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    generators = "CMakeToolchain", "CMakeDeps"
    package_type = "header-library"

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package(self):
        copy(
            self,
            "LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            "qc-hash.hpp",
            self.source_folder,
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

    def package_id(self):
        self.info.clear()
