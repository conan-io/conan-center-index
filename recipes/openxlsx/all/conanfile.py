from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class OpenXlsxConan(ConanFile):
    name = "openxlsx"
    description = "reading, writing, creating and modifying Microsoft Excel® (.xlsx) files."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/troldal/OpenXLSX"
    topics = ("excel", "spreadsheet", "xlsx")
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

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "9",
            "clang": "9",
            "apple-clang": "12",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OPENXLSX_CREATE_DOCS"] = False
        tc.variables["OPENXLSX_BUILD_SAMPLES"] = False
        tc.variables["OPENXLSX_BUILD_TESTS"] = False
        tc.variables["OPENXLSX_BUILD_BENCHMARKS"] = False
        tc.variables["OPENXLSX_LIBRARY_TYPE"] = "SHARED" if self.options.shared else "STATIC"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        lib_suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"OpenXLSX{lib_suffix}"]

        self.cpp_info.set_property("cmake_file_name", "OpenXLSX")
        self.cpp_info.set_property("cmake_target_name", "OpenXLSX::OpenXLSX")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenXLSX"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenXLSX"
        self.cpp_info.names["cmake_find_package"] = "OpenXLSX"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenXLSX"
