from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, load, rm, rmdir, save
from conan.tools.scm import Version
import os

import yaml

required_conan_version = ">=1.53.0"

#
# INFO: Please, remove all comments before pushing your PR!
#

class _Library:
    name: str
    deps: list[str]

class FuzztestConan(ConanFile):
    name = "fuzztest"
    description = "A C++ testing framework for writing and executing fuzz tests"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/fuzztest"
    topics = ("fuzzing", "testing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    def export_sources(self):
        copy(self, f"_package_info-{self.version}.yml",
             os.path.join(self.recipe_folder, "package_info"),
             os.path.join(self.export_sources_folder))

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
#    @property
#    def _compilers_minimum_version(self):
#        return {
#            "apple-clang": "10",
#            "clang": "7",
#            "gcc": "7",
#            "msvc": "191",
#            "Visual Studio": "15",
#        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("abseil/20240116.1@local/beta", force=True) # Waiting on PR
        self.requires("antlr4-cppruntime/4.13.1")
        self.requires("gtest/1.14.0")
        self.requires("re2/20240301@local/beta", force=True) # Waiting on PR, uses internal headers

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if self.settings.compiler not in ["gcc", "clang", "apple-clang"]:
            raise ConanInvalidConfiguration(f"{self.ref} only supports GCC and (Apple) Clang")
#        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
#        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
#            raise ConanInvalidConfiguration(
#                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
#            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _fetchcontent_to_findpackage(self):
        # Replace the entirety of the FetchContent-based dependency fetching with find_packages
        save(self, os.path.join(self.source_folder, "cmake", "BuildDependencies.cmake"), """
find_package(re2 REQUIRED CONFIG)
find_package(absl REQUIRED CONFIG)
find_package(GTest REQUIRED CONFIG)
find_package(antlr4-runtime REQUIRED CONFIG)
""")

    def build(self):
        self._fetchcontent_to_findpackage()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        info_path = os.path.join(self.export_sources_folder, f"_package_info-{self.version}.yml")
        info = yaml.safe_load(open(info_path, "r"))

        for name, data in info.items():
            if not data["header_only"]:
                # Just assuming Linux/static for a minute
                copy(self, f"*{name}*.a", os.path.join(self.build_folder, "fuzztest"), os.path.join(self.package_folder, "lib"))
                print(name)
            # TODO add an assertion to make sure no compiled libraries get missed
            #print(name)
            #print(data["header_only"])
            #print(data["deps"])

        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        pass # TODO
#        self.cpp_info.libs = ["package_lib"]
#
#        # if package has an official FindPACKAGE.cmake listed in https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules
#        # examples: bzip2, freetype, gdal, icu, libcurl, libjpeg, libpng, libtiff, openssl, sqlite3, zlib...
#        self.cpp_info.set_property("cmake_module_file_name", "PACKAGE")
#        self.cpp_info.set_property("cmake_module_target_name", "PACKAGE::PACKAGE")
#        # if package provides a CMake config file (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
#        self.cpp_info.set_property("cmake_file_name", "package")
#        self.cpp_info.set_property("cmake_target_name", "package::package")
#        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
#        self.cpp_info.set_property("pkg_config_name", "package")
#
#        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
#        if self.settings.os in ["Linux", "FreeBSD"]:
#            self.cpp_info.system_libs.append("m")
#            self.cpp_info.system_libs.append("pthread")
#            self.cpp_info.system_libs.append("dl")
#
#        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
#        self.cpp_info.filenames["cmake_find_package"] = "PACKAGE"
#        self.cpp_info.filenames["cmake_find_package_multi"] = "package"
#        self.cpp_info.names["cmake_find_package"] = "PACKAGE"
#        self.cpp_info.names["cmake_find_package_multi"] = "package"
