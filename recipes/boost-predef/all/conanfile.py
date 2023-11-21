from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches,
    get, mkdir, rename, rm, rmdir
)
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import glob
import os

required_conan_version = ">=1.53.0"

class BoostPredefConan(ConanFile):
    name = "boost-predef"
    description = "This library defines a set of compiler, architecture, operating system, library, and other version numbers from the information it can gather of C, C++, Objective C, and Objective C++ predefined macros or those defined in generally available headers."
    url = "https://github.com/boostorg/predef"
    homepage = "https://www.boost.org"
    license = "BSL-1.0"
    topics = ("libraries", "cpp")

    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = {}

    short_paths = True
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        pass

    def configure(self):
        pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def requirements(self):
        pass

    def package_id(self):
        self.info.clear()

    def build_requirements(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(
            self,
            "*",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.env_info.BOOST_ROOT = self.package_folder

        self.cpp_info.set_property("cmake_file_name", "Boost")
        self.cpp_info.filenames["cmake_find_package"] = "Boost"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Boost"
        self.cpp_info.names["cmake_find_package"] = "Boost"
        self.cpp_info.names["cmake_find_package_multi"] = "Boost"

        # - Use 'predef' component for all includes + defines

        self.cpp_info.components["predef"].libs = []
        self.cpp_info.components["predef"].libdirs = []
        self.cpp_info.components["predef"].set_property("cmake_target_name", "Boost::predef")
        self.cpp_info.components["predef"].names["cmake_find_package"] = "predef"
        self.cpp_info.components["predef"].names["cmake_find_package_multi"] = "predef"
        self.cpp_info.components["predef"].names["pkg_config"] = "boost"

        # # Boost::boost is an alias of Boost::predef
        # self.cpp_info.components["_boost_cmake"].requires = ["predef"]
        # self.cpp_info.components["_boost_cmake"].set_property("cmake_target_name", "Boost::boost")
        # self.cpp_info.components["_boost_cmake"].names["cmake_find_package"] = "boost"
        # self.cpp_info.components["_boost_cmake"].names["cmake_find_package_multi"] = "boost"

        # if self.options.header_only:
        # self.cpp_info.components["_boost_cmake"].libdirs = []
