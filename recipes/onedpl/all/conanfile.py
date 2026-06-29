from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2"


class OneDplConan(ConanFile):
    name = "onedpl"
    description = ("OneDPL (Formerly Parallel STL) is an implementation of "
                   "the C++ standard library algorithms"
                   "with support for execution policies, as specified in "
                   "ISO/IEC 14882:2017 standard, commonly called C++17")
    license = "Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneDPL"
    topics = ("stl", "parallelism")
    package_type = "header-library"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "backend": ["tbb", "serial"],
    }
    default_options = {
        "backend": "tbb",
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.backend == "tbb":
            self.requires("onetbb/[>=2021.10.0 <2024]")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE.txt", src=os.path.join(self.source_folder, "licensing"), dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ParallelSTL")
        self.cpp_info.set_property("cmake_target_name", "pstl::ParallelSTL")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.components["_onedpl"].set_property("cmake_target_name", "pstl::ParallelSTL")
        self.cpp_info.components["_onedpl"].bindirs = []
        self.cpp_info.components["_onedpl"].libdirs = []
        if self.options.backend == "tbb":
            self.cpp_info.components["_onedpl"].requires = ["onetbb::libtbb"]
