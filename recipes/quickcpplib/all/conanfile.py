import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, default_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import (
    get, copy, rmdir, rm, apply_conandata_patches,
    export_conandata_patches
)
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class QuickcpplibCodeConan(ConanFile):
    name = "quickcpplib"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/quickcpplib"
    description = "@ned14: Eliminate all the tedious hassle when making state-of-the-art C++ 17 - 23 libraries!"
    topics = ("header-only",  "common")
    package_type = "header-library"
    settings = "os", "arch", "build_type", "compiler"

    @property
    def _compiler_required_version(self):
        return {
            "gcc": "9",
            "clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    @property
    def _pure_cppstd(self):
        applied_cppstd = self.settings.compiler.get_safe("cppstd")
        if not applied_cppstd:
            applied_cppstd = default_cppstd(self)

        if applied_cppstd:
            return str(applied_cppstd).replace("gnu", "")

        return "17"

    @property
    def _needs_span_lite(self):
        return self._pure_cppstd < "20"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self._needs_span_lite:
            self.requires("span-lite/0.10.3")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            # To simplify library integration to CCI
            # we require C++17 to be dependency free.
            check_min_cppstd(self, "17")

        min_version = self._compiler_required_version.get(str(self.settings.compiler))
        if min_version:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        else:
            self.output.warning("This recipe has no support for the current compiler. Please consider adding it.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        pass

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.ipp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "include", "quickcpplib", "byte" ))
        rmdir(self, os.path.join(self.package_folder, "include", "quickcpplib", "boost" ))
        rmdir(self, os.path.join(self.package_folder, "include", "quickcpplib", "optional" ))
        rmdir(self, os.path.join(self.package_folder, "include", "quickcpplib", "span-lite" ))
        rm(self, "allocator_testing.hpp", os.path.join(self.package_folder, "include", "quickcpplib"))
        copy(self, "Licence.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "quickcpplib")
        self.cpp_info.set_property("cmake_target_name", "quickcpplib::hl")

        self.cpp_info.components["quickcpplib_hl"].set_property("cmake_target_name", "quickcpplib::hl")
        if self._needs_span_lite:
            self.cpp_info.components["quickcpplib_hl"].requires = ["span-lite::span-lite"]

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["quickcpplib_hl"].system_libs = ["dl", "pthread", "rt"]

        self.cpp_info.components["quickcpplib_hl"].defines.append("QUICKCPPLIB_DISABLE_ABI_PERMUTATION")

        if not self._needs_span_lite:
            self.cpp_info.components["quickcpplib_hl"].defines.append("QUICKCPPLIB_USE_STD_SPAN=1")

        self.cpp_info.components["quickcpplib_hl"].defines.append("QUICKCPPLIB_USE_STD_BYTE=1")
        self.cpp_info.components["quickcpplib_hl"].defines.append("QUICKCPPLIB_USE_STD_OPTIONAL=1")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "quickcpplib"
        self.cpp_info.filenames["cmake_find_package_multi"] = "quickcpplib"
        self.cpp_info.names["cmake_find_package"] = "quickcpplib"
        self.cpp_info.names["cmake_find_package_multi"] = "quickcpplib"
        self.cpp_info.components["hl"].names["cmake_find_package"] = "quickcpplib"
        self.cpp_info.components["hl"].names["cmake_find_package_multi"] = "quickcpplib"
        self.cpp_info.components["hl"].defines.append("QUICKCPPLIB_DISABLE_ABI_PERMUTATION")
        self.cpp_info.components["hl"].defines.append("QUICKCPPLIB_USE_STD_BYTE=1")
        self.cpp_info.components["hl"].defines.append("QUICKCPPLIB_USE_STD_OPTIONAL=1")
        if not self._needs_span_lite:
            self.cpp_info.components["hl"].defines.append("QUICKCPPLIB_USE_STD_SPAN=1")
        self.cpp_info.components["hl"].set_property("cmake_target_name", "quickcpplib::hl")
        self.cpp_info.components["hl"].bindirs = []
        self.cpp_info.components["hl"].libdirs = []
        self.cpp_info.components["hl"].resdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["hl"].system_libs = ["dl", "pthread", "rt"]
