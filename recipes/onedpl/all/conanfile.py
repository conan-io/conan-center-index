from conans import ConanFile, tools
from conan.tools import files
import os

required_conan_version = ">=1.43.0"


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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.backend == "tbb":
            self.requires("onetbb/2020.3")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if tools.Version(self.version) >= "2021.7.0":
                tools.check_min_cppstd(self, 17)
            else:
                tools.check_min_cppstd(self, 11)

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        version_major = int(tools.Version(self.version).major[0:4])
        self.copy("*", src=os.path.join(self._source_subfolder, "include"), dst="include")
        if version_major < 2021:
            self.copy("*", src=os.path.join(self._source_subfolder, "stdlib"), dst="include")
            self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        else:
            self.copy("LICENSE.txt", src=os.path.join(self._source_subfolder, "licensing"), dst="licenses")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ParallelSTL")
        self.cpp_info.set_property("cmake_target_name", "pstl::ParallelSTL")

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
