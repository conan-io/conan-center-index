from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class OneDplConan(ConanFile):
    name = "onedpl"
    description = ("OneDPL (Formerly Parallel STL) is an implementation of "
                   "the C++ standard library algorithms"
                   "with support for execution policies, as specified in "
                   "ISO/IEC 14882:2017 standard, commonly called C++17")
    license = ("Apache-2.0", "LLVM-exception")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneDPL"
    topics = ("stl", "parallelism")
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "backend": ["tbb", "serial"],
    }
    default_options = {
        "backend": "tbb",
    }
    no_copy_source = True

    def requirements(self):
        if self.options.backend == "tbb":
            self.requires("onetbb/2020.3")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if Version(self.version) >= "2021.7.0":
                check_min_cppstd(self, 17)
            else:
                check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def package(self):
        version_major = int(Version(self.version).major[0:4])
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        if version_major < 2021:
            copy(self, "*", src=os.path.join(self.source_folder, "stdlib"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        else:
            copy(self, "LICENSE.txt", src=os.path.join(self.source_folder, "licensing"), dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ParallelSTL")
        self.cpp_info.set_property("cmake_target_name", "pstl::ParallelSTL")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "ParallelSTL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ParallelSTL"
        self.cpp_info.names["cmake_find_package"] = "pstl"
        self.cpp_info.names["cmake_find_package_multi"] = "pstl"
        self.cpp_info.components["_onedpl"].names["cmake_find_package"] = "ParallelSTL"
        self.cpp_info.components["_onedpl"].names["cmake_find_package_multi"] = "ParallelSTL"
        self.cpp_info.components["_onedpl"].set_property("cmake_target_name", "pstl::ParallelSTL")
        if self.options.backend == "tbb":
            self.cpp_info.components["_onedpl"].requires = ["onetbb::onetbb"]
