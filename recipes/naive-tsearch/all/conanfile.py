from conan import ConanFile
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class NaiveTsearchConan(ConanFile):
    name = "naive-tsearch"
    description = "A simple tsearch() implementation for platforms without one"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kulp/naive-tsearch"
    topics = ("tsearch", "search", "tree", "msvc")
    package_type = 'static-library'
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "fPIC": True,
        "header_only": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
        if self.options.header_only:
            self.package_type = 'header-library'

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()
        else:
            del self.info.options.header_only

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NAIVE_TSEARCH_INSTALL"] = True
        tc.variables["NAIVE_TSEARCH_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.options.header_only:
            rmdir(self, os.path.join(self.package_folder, "lib"))
            rm(self, "tsearch.h", os.path.join(self.package_folder, "include", "naive-tsearch"))
        else:
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "tsearch_hdronly.h", os.path.join(self.package_folder, "include", "naive-tsearch"))
            rm(self, "tsearch.c.inc", os.path.join(self.package_folder, "include", "naive-tsearch"))

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.components["header_only"].libs = []
            self.cpp_info.components["header_only"].libdirs = []
            self.cpp_info.components["header_only"].bindirs = []
            self.cpp_info.components["header_only"].includedirs.append(os.path.join("include", "naive-tsearch"))
            self.cpp_info.components["header_only"].defines = ["NAIVE_TSEARCH_HDRONLY"]
            self.cpp_info.components["header_only"].set_property("cmake_target_name", "naive-tsearch::naive-tsearch-hdronly")
            self.cpp_info.components["header_only"].set_property("pkg_config_name", "naive-tsearch")
        else:
            self.cpp_info.components["naive_tsearch"].libs = ["naive-tsearch"]
            self.cpp_info.components["naive_tsearch"].includedirs.append(os.path.join("include", "naive-tsearch"))
            self.cpp_info.components["naive_tsearch"].set_property("cmake_target_name", "naive-tsearch::naive-tsearch")
            self.cpp_info.components["naive_tsearch"].set_property("pkg_config_name", "naive-tsearch")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        if self.options.header_only:
            self.cpp_info.components["header_only"].names["cmake_find_package"] = "naive-tsearch-hdronly"
            self.cpp_info.components["header_only"].names["cmake_find_package_multi"] = "naive-tsearch-hdronly"
        else:
            self.cpp_info.components["naive_tsearch"].names["cmake_find_package"] = "naive-tsearch"
            self.cpp_info.components["naive_tsearch"].names["cmake_find_package_multi"] = "naive-tsearch"
