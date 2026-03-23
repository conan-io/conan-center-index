from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.0"


class CavalierContoursConan(ConanFile):
    name = "cavalier-contours"
    description = (
        "C++14 header-only library for processing 2D polylines containing "
        "straight line and constant radius arc segments. Supports contour/parallel "
        "offsetting and boolean operations (OR, AND, NOT, XOR) between closed polylines."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jbuckmccready/CavalierContours"
    topics = ("geometry", "polyline", "offset", "cad", "cam", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CavalierContours")
        self.cpp_info.set_property("cmake_target_name", "CavalierContours::CavalierContours")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
