from conan import ConanFile
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=2.4"


class TriangleMeshDistanceConan(ConanFile):
    name = "trianglemeshdistance"
    description = "Header only, single file, simple and efficient C++11 library to compute the signed distance function (SDF) to a triangle mesh"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/InteractiveComputerGraphics/TriangleMeshDistance"
    topics = ("simulation", "geometry", "graphics", "distance", "triangle",  "collision-detection", "mesh", "sdf", "level-set", "signed-distance-fields")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    implements = ["auto_header_only"]


    def layout(self):
        basic_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "tmd/TriangleMeshDistance.h",  src=os.path.join(self.source_folder, "TriangleMeshDistance", "include"),  dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TriangleMeshDistance")
        self.cpp_info.set_property("cmake_target_name", "trianglemeshdistance::trianglemeshdistance")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
