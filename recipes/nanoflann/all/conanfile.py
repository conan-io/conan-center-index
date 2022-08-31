from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class NanoflannConan(ConanFile):
    name = "nanoflann"
    description = """nanoflann is a C++11 header-only library for building KD-Trees
                    of datasets with different topologies: R2, R3 (point clouds),
                    SO(2) and SO(3) (2D and 3D rotation groups).
                    """
    topics = ("nanoflann", "nearest-neighbor", "kd-trees")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jlblancoc/nanoflann"
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        include_folder = os.path.join(self.source_folder, "include")
        copy(self, "*", src=include_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nanoflann")
        self.cpp_info.set_property("cmake_target_name", "nanoflann::nanoflann")
        self.cpp_info.set_property("pkg_config_name", "nanoflann")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
