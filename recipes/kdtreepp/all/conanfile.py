import os
from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0"


class KdTreePpConan(ConanFile):
    name = "kdtreepp"
    package_type = "header-library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jhurliman/kdtreepp"
    topics = ("header-only", "spatial-index", "nearest-neighbor", "eigen")
    settings = "os", "arch", "compiler", "build_type"
    description = "A header-only C++17 k-d tree for Eigen"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True)

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "kdtreepp")
        self.cpp_info.set_property("cmake_target_name", "kdtreepp::kdtreepp")
