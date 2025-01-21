from conan import ConanFile
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=2.0"

class ScnlibConan(ConanFile):
    name = "scnlib"
    description = "scanf for modern C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eliaskosunen/scnlib"
    topics = ("parsing", "io", "scanf")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "header_only": [True, False],
        "shared": [True, False],
        "fPIC": [True, False],
        "regex_backend": ["None", "std", "boost", "boost_icu", "re2"],
    }
    default_options = {
        "header_only": False,
        "shared": False,
        "fPIC": True,
        "regex_backend": "std",
    }

    @property
    def _min_cppstd(self):
        # scn/2.0.0 has complation error on MSVC c++17
        # we have to use versions which support c++20
        # https://github.com/eliaskosunen/scnlib/issues/97
        # https://github.com/conan-io/conan-center-index/pull/22455#issuecomment-1924444193
        return "20" if is_msvc(self) else "17"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("header_only") or self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.get_safe("header_only"):
            del self.options.shared
            self.package_type = "header-library"

    def layout(self):
        if self.options.get_safe("header_only"):
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("fast_float/6.1.0")
        if Version(self.version) < "3.0":
            self.requires("simdutf/4.0.5")
        if self.options.get_safe("regex_backend") in ["boost", "boost_icu"]:
            self.requires("boost/1.83.0")
        elif self.options.get_safe("regex_backend") == "re2":
            self.requires("re2/20231101")

    def package_id(self):
        if self.info.options.get_safe("header_only"):
            self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

        if self.options.get_safe("regex_backend") == "boost_icu" and \
            not self.dependencies["boost"].options.get_safe("i18n_backend_icu"):
            raise ConanInvalidConfiguration(
                f"{self.ref} with regex_backend=Boost_icu option requires boost::i18n_backend_icu to be enabled."
            )
        # TODO: This should probably be a del self.options.header_only in config_options once the CI supports it
        if self.options.header_only:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support header only mode.")
        if Version(self.version) < "3.0.2" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "11":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support gcc 11.x due to std::regex_constants::multiline is not defined.")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.get_safe("header_only"):
            return

        tc = CMakeToolchain(self)
        tc.variables["SCN_TESTS"] = False
        tc.variables["SCN_EXAMPLES"] = False
        tc.variables["SCN_BENCHMARKS"] = False
        tc.variables["SCN_DOCS"] = False
        tc.variables["SCN_INSTALL"] = True
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True

        tc.variables["SCN_USE_EXTERNAL_SIMDUTF"] = True
        tc.variables["SCN_USE_EXTERNAL_FAST_FLOAT"] = True
        tc.variables["SCN_BENCHMARKS_BUILDTIME"] = False
        tc.variables["SCN_BENCHMARKS_BINARYSIZE"] = False
        tc.variables["SCN_DISABLE_REGEX"] = self.options.regex_backend is None
        if self.options.regex_backend is not None:
            tc.variables["SCN_REGEX_BACKEND"] = self.options.regex_backend
            tc.variables["SCN_USE_EXTERNAL_REGEX_BACKEND"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        if not self.options.get_safe("header_only"):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.get_safe("header_only"):
            copy(self, "*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
            src_folder = os.path.join(self.source_folder, "src")
            copy(self, "reader_*.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "reader"))
            copy(self, "vscan.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "scan"))
            copy(self, "locale.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "detail"))
            copy(self, "file.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "detail"))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.cmake", os.path.join(self.package_folder, "include", "scn", "detail"))
        rmdir(self, os.path.join(self.package_folder, "include", "scn", "detail", "CMakeFiles"))
        rmdir(self, os.path.join(self.package_folder, "include", "scn", "detail", "deps", "CMakeFiles"))

    def package_info(self):
        target = "scn-header-only" if self.options.get_safe("header_only") else "scn"
        self.cpp_info.set_property("cmake_file_name", "scn")
        self.cpp_info.set_property("cmake_target_name", f"scn::{target}")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        if self.options.get_safe("header_only"):
            self.cpp_info.components["_scnlib"].defines = ["SCN_HEADER_ONLY=1"]
        else:
            self.cpp_info.components["_scnlib"].defines = ["SCN_HEADER_ONLY=0"]
            self.cpp_info.components["_scnlib"].libs = ["scn"]
        self.cpp_info.components["_scnlib"].requires.append("fast_float::fast_float")
        if Version(self.version) < "3.0":
            self.cpp_info.components["_scnlib"].requires.append("simdutf::simdutf")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_scnlib"].system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "scn"
        self.cpp_info.names["cmake_find_package_multi"] = "scn"
        self.cpp_info.components["_scnlib"].names["cmake_find_package"] = target
        self.cpp_info.components["_scnlib"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["_scnlib"].set_property("cmake_target_name", f"scn::{target}")
