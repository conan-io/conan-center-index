from conan import ConanFile
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.54.0"


class LibheifConan(ConanFile):
    name = "libheif"
    description = "libheif is an HEIF and AVIF file format decoder and encoder."
    topics = ("heif", "codec", "video")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/strukturag/libheif"
    license = ("LGPL-3.0-only", "GPL-3.0-or-later", "MIT")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libde265": [True, False],
        "with_x265": [True, False],
        "with_libaomav1": [True, False],
        "with_dav1d": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libde265": True,
        "with_x265": False,
        "with_libaomav1": False,
        "with_dav1d": False,
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
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libde265:
            self.requires("libde265/1.0.9")
        if self.options.with_x265:
            self.requires("libx265/3.4")
        if self.options.with_libaomav1:
            self.requires("libaom-av1/3.5.0")
        if self.options.with_dav1d:
            self.requires("dav1d/1.0.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_LIBDE265"] = self.options.with_libde265
        tc.variables["WITH_X265"] = self.options.with_x265
        tc.variables["WITH_AOM"] = self.options.with_libaomav1
        tc.variables["WITH_RAV1E"] = False
        tc.variables["WITH_DAV1D"] = self.options.with_dav1d
        tc.variables["WITH_EXAMPLES"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libheif")
        self.cpp_info.set_property("cmake_target_name", "libheif::heif")
        self.cpp_info.set_property("pkg_config_name", "libheif")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["heif"].libs = ["heif"]
        if not self.options.shared:
            self.cpp_info.components["heif"].defines = ["LIBHEIF_STATIC_BUILD"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["heif"].system_libs.extend(["m", "pthread"])
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["heif"].system_libs.append(libcxx)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["heif"].set_property("cmake_target_name", "libheif::heif")
        self.cpp_info.components["heif"].set_property("pkg_config_name", "libheif")
        self.cpp_info.components["heif"].requires = []
        if self.options.with_libde265:
            self.cpp_info.components["heif"].requires.append("libde265::libde265")
        if self.options.with_x265:
            self.cpp_info.components["heif"].requires.append("libx265::libx265")
        if self.options.with_libaomav1:
            self.cpp_info.components["heif"].requires.append("libaom-av1::libaom-av1")
        if self.options.with_dav1d:
            self.cpp_info.components["heif"].requires.append("dav1d::dav1d")
