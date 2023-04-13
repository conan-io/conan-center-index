from conan import ConanFile
from conan.tools.microsoft import check_min_vs
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.53.0"

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
    }
    default_options = {
        "header_only": False,
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only or self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.header_only:
            del self.options.shared

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "1.0":
            self.requires("fast_float/4.0.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192 if Version(self.version) >= "1.0" else 191)

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if self.options.header_only:
            return

        tc = CMakeToolchain(self)
        tc.variables["SCN_TESTS"] = False
        tc.variables["SCN_EXAMPLES"] = False
        tc.variables["SCN_BENCHMARKS"] = False
        tc.variables["SCN_DOCS"] = False
        tc.variables["SCN_INSTALL"] = True
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if Version(self.version) >= "1.0":
            tc.variables["SCN_USE_BUNDLED_FAST_FLOAT"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.header_only:
            copy(self, "*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
            src_folder = os.path.join(self.source_folder, "src")
            if Version(self.version) >= "1.0":
                copy(self, "reader_*.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "reader"))
                copy(self, "vscan.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "scan"))
                copy(self, "locale.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "detail"))
                copy(self, "file.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "detail"))
            else:
                copy(self, "*.cpp", src=src_folder, dst=os.path.join(self.package_folder, "include", "scn", "detail"))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "share"))
        if Version(self.version) >= "1.0":
            rm(self, "*.cmake", os.path.join(self.package_folder, "include", "scn", "detail"))
            rmdir(self, os.path.join(self.package_folder, "include", "scn", "detail", "CMakeFiles"))
            rmdir(self, os.path.join(self.package_folder, "include", "scn", "detail", "deps", "CMakeFiles"))

    def package_info(self):
        target = "scn-header-only" if self.options.header_only else "scn"
        self.cpp_info.set_property("cmake_file_name", "scn")
        self.cpp_info.set_property("cmake_target_name", f"scn::{target}")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        if self.options.header_only:
            self.cpp_info.components["_scnlib"].defines = ["SCN_HEADER_ONLY=1"]
        else:
            self.cpp_info.components["_scnlib"].defines = ["SCN_HEADER_ONLY=0"]
            self.cpp_info.components["_scnlib"].libs = ["scn"]
        if Version(self.version) >= "1.0":
            self.cpp_info.components["_scnlib"].requires = ["fast_float::fast_float"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_scnlib"].system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "scn"
        self.cpp_info.names["cmake_find_package_multi"] = "scn"
        self.cpp_info.components["_scnlib"].names["cmake_find_package"] = target
        self.cpp_info.components["_scnlib"].names["cmake_find_package_multi"] = target
        self.cpp_info.components["_scnlib"].set_property("cmake_target_name", f"scn::{target}")
