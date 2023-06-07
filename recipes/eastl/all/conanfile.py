import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
)
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class EastlConan(ConanFile):
    name = "eastl"
    description = (
        "EASTL stands for Electronic Arts Standard Template Library. "
        "It is an extensive and robust implementation that has an "
        "emphasis on high performance."
    )
    topics = ("eastl", "stl", "high-performance")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/electronicarts/EASTL"

    package_type = "header-library"
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
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "14",
            "gcc": "6",
            "clang": "6",
            "apple-clang": "6",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eabase/2.09.12")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True,
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EASTL_BUILD_BENCHMARK"] = False
        tc.variables["EASTL_BUILD_TESTS"] = False
        tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.generate()
        CMakeDeps(self).generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "include(CommonCppFlags)",
            "",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "3RDPARTYLICENSES.TXT",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if self.options.shared:
            self.cpp_info.defines.append("EA_DLL")

        self.cpp_info.set_property("cmake_file_name", "EASTL")
        self.cpp_info.set_property("cmake_target_name", "EASTL::EASTL")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "EASTL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "EASTL"
        self.cpp_info.names["cmake_find_package"] = "EASTL"
        self.cpp_info.names["cmake_find_package_multi"] = "EASTL"
