from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

class KDAlgorithmsConan(ConanFile):
    name = "kdalgorithmns"
    license = "MIT"
    description = "C++ Algorithm wrappers"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KDAB/KDAlgorithms"
    topics = ("c++14", "algorithmns", "kdab", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        # src_folder must use the same source folder name than the project
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        check_min_cppstd(self, "14")

    def package(self):
        copy(self, "*.h", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "include", "kdalgorithmns"))
        copy(self, "LICENSES/*", dst=os.path.join(self.package_folder,"licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = ["include/kdalgorithmns"]
        self.cpp_info.set_property("cmake_file_name", "KDAlgorithms")
        self.cpp_info.set_property("cmake_target_name", "KDAB::KDAlgorithms")
        self.cpp_info.set_property("cmake_target_aliases", ["KDAlgorithms"])
