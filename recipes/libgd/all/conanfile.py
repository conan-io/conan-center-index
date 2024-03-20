from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class LibgdConan(ConanFile):
    name = "libgd"
    description = ("GD is an open source code library for the dynamic"
                   "creation of images by programmers.")
    license = "BSD-like"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libgd.github.io"
    topics = ("images", "graphics")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_jpeg": [True, False],
        "with_tiff": [True, False],
        "with_freetype": [True, False],
        "with_xpm": [True, False],
        "with_webp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": False,
        "with_jpeg": False,
        "with_tiff": False,
        "with_freetype": False,
        "with_xpm": False,
        "with_webp": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
            if is_msvc(self):
                self.requires("getopt-for-visual-studio/20200201")
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.with_xpm:
            self.requires("libxpm/3.5.13")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_C_STANDARD"] = "99"
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        if Version(self.version) >= "2.3.0":
            tc.variables["ENABLE_GD_FORMATS"] = True
        tc.variables["ENABLE_PNG"] = self.options.with_png
        tc.variables["ENABLE_LIQ"] = False
        tc.variables["ENABLE_JPEG"] = self.options.with_jpeg
        tc.variables["ENABLE_TIFF"] = self.options.with_tiff
        tc.variables["ENABLE_ICONV"] = False
        tc.variables["ENABLE_XPM"] =  self.options.with_xpm
        tc.variables["ENABLE_FREETYPE"] = self.options.with_freetype
        tc.variables["ENABLE_FONTCONFIG"] = False
        tc.variables["ENABLE_WEBP"] = self.options.with_webp
        if Version(self.version) >= "2.3.2":
            tc.variables["ENABLE_HEIF"] = False
            tc.variables["ENABLE_AVIF"] = False
        if Version(self.version) >= "2.3.0":
            tc.variables["ENABLE_RAQM"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "${CMAKE_SOURCE_DIR}",
                        "${CMAKE_CURRENT_SOURCE_DIR}")
        replace_in_file(self, cmakelists,
                        "SET(CMAKE_MODULE_PATH \"${GD_SOURCE_DIR}/cmake/modules\")",
                        "LIST(APPEND CMAKE_MODULE_PATH \"${GD_SOURCE_DIR}/cmake/modules\")")
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                        "RUNTIME DESTINATION bin",
                        "RUNTIME DESTINATION bin BUNDLE DESTINATION bin")

    def build(self):
        self._patch()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        prefix_libs = "lib" if self.settings.os == "Windows" else ""
        suffix_libs = "_static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = [f"{prefix_libs}gd{suffix_libs}"]
        self.cpp_info.set_property("pkg_config_name", "gdlib")

        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("BGD_NONDLL")
            self.cpp_info.defines.append("BGDWIN32")
        if self.settings.os in ("FreeBSD", "Linux", "Android", "SunOS", "AIX"):
            self.cpp_info.system_libs.append("m")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["pkg_config"]= "gdlib"
