from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.47.0"


class LibwebpConan(ConanFile):
    name = "libwebp"
    description = "Library to encode and decode images in WebP format"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/webmproject/libwebp"
    topics = ("image", "libwebp", "webp", "decoding", "encoding")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_simd": [True, False],
        "near_lossless": [True, False],
        "swap_16bit_csp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_simd": True,
        "near_lossless": True,
        "swap_16bit_csp": False,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # should be an option but it doesn't work yet
        tc.variables["WEBP_ENABLE_SIMD"] = self.options.with_simd
        if Version(self.version) >= "1.0.0":
            tc.variables["WEBP_NEAR_LOSSLESS"] = self.options.near_lossless
        else:
            tc.variables["WEBP_ENABLE_NEAR_LOSSLESS"] = self.options.near_lossless
        tc.variables["WEBP_ENABLE_SWAP_16BIT_CSP"] = self.options.swap_16bit_csp
        # avoid finding system libs
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_GIF"] = True
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_PNG"] = True
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_TIFF"] = True
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_JPEG"] = True
        tc.variables["WEBP_BUILD_ANIM_UTILS"] = False
        tc.variables["WEBP_BUILD_CWEBP"] = False
        tc.variables["WEBP_BUILD_DWEBP"] = False
        tc.variables["WEBP_BUILD_IMG2WEBP"] = False
        tc.variables["WEBP_BUILD_GIF2WEBP"] = False
        tc.variables["WEBP_BUILD_VWEBP"] = False
        tc.variables["WEBP_BUILD_EXTRAS"] = False
        tc.variables["WEBP_BUILD_WEBPINFO"] = False
        if Version(self.version) >= "1.2.1":
            tc.variables["WEBP_BUILD_LIBWEBPMUX"] = True
        tc.variables["WEBP_BUILD_WEBPMUX"] = False
        if self.options.shared and is_msvc(self):
          # Building a dll (see fix-dll-export patch)
          tc.preprocessor_definitions["WEBP_DLL"] = 1
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "WebP")
        self.cpp_info.set_property("pkg_config_name", "libwebp-all-do-not-use")

        # webpdecoder
        self.cpp_info.components["webpdecoder"].set_property("cmake_target_name", "WebP::webpdecoder")
        self.cpp_info.components["webpdecoder"].set_property("pkg_config_name", "libwebpdecoder")
        self.cpp_info.components["webpdecoder"].libs = ["webpdecoder"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["webpdecoder"].system_libs = ["pthread"]

        # webp
        self.cpp_info.components["webp"].set_property("cmake_target_name", "WebP::webp")
        self.cpp_info.components["webp"].set_property("pkg_config_name", "libwebp")
        self.cpp_info.components["webp"].libs = ["webp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["webp"].system_libs = ["m", "pthread"]

        # webpdemux
        self.cpp_info.components["webpdemux"].set_property("cmake_target_name", "WebP::webpdemux")
        self.cpp_info.components["webpdemux"].set_property("pkg_config_name", "libwebpdemux")
        self.cpp_info.components["webpdemux"].libs = ["webpdemux"]
        self.cpp_info.components["webpdemux"].requires = ["webp"]

        # webpmux
        self.cpp_info.components["webpmux"].set_property("cmake_target_name", "WebP::libwebpmux")
        self.cpp_info.components["webpmux"].set_property("pkg_config_name", "libwebpmux")
        self.cpp_info.components["webpmux"].libs = ["webpmux"]
        self.cpp_info.components["webpmux"].requires = ["webp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["webpmux"].system_libs = ["m"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "WebP"
        self.cpp_info.names["cmake_find_package_multi"] = "WebP"
        self.cpp_info.names["pkg_config"] = "libwebp-all-do-not-use"
        self.cpp_info.components["webpmux"].names["cmake_find_package"] = "libwebpmux"
        self.cpp_info.components["webpmux"].names["cmake_find_package_multi"] = "libwebpmux"
