from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class LibheifConan(ConanFile):
    name = "libheif"
    description = "libheif is an HEIF and AVIF file format decoder and encoder."
    license = ("LGPL-3.0-only", "GPL-3.0-or-later", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/strukturag/libheif"
    topics = ("heif", "codec", "video")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libde265": [True, False],
        "with_x265": [True, False],
        "with_libaomav1": [True, False],
        "with_dav1d": [True, False],
        "with_jpeg": [True, False],
        "with_openjpeg": [True, False],
        "with_openjph": [True, False],
        "with_openh264": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libde265": True,
        "with_x265": False,
        "with_libaomav1": False,
        "with_dav1d": False,
        "with_jpeg": False,
        "with_openjpeg": False,
        "with_openjph": False,
        "with_openh264": False,
    }

    @property
    def _min_cppstd(self):
        return "20" if Version(self.version) >= "1.19.0" else "11"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.17.0":
            del self.options.with_jpeg
            del self.options.with_openjpeg
        if Version(self.version) < "1.18.0":
            del self.options.with_openjph
        if Version(self.version) < "1.19.0":
            del self.options.with_openh264

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libde265:
            self.requires("libde265/1.0.12")
        if self.options.with_x265:
            self.requires("libx265/3.4")
        if self.options.with_libaomav1:
            self.requires("libaom-av1/3.6.1")
        if self.options.with_dav1d:
            self.requires("dav1d/1.2.1")
        if self.options.get_safe("with_jpeg"):
            self.requires("libjpeg/9f")
        if self.options.get_safe("with_openjpeg"):
            self.requires("openjpeg/2.5.2")
        if self.options.get_safe("with_openjph"):
            self.requires("openjph/0.16.0", transitive_headers=False)
        if self.options.get_safe("with_openh264"):
            self.requires("openh264/2.4.1")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def build_requirements(self):
        if Version(self.version) >= "1.18.0":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_LIBSHARPYUV"] = False
        tc.variables["WITH_LIBDE265"] = self.options.with_libde265
        tc.variables["WITH_X265"] = self.options.with_x265
        tc.variables["WITH_AOM"] = self.options.with_libaomav1
        tc.variables["WITH_AOM_DECODER"] = self.options.with_libaomav1
        tc.variables["WITH_AOM_ENCODER"] = self.options.with_libaomav1
        tc.variables["WITH_RAV1E"] = False
        tc.variables["WITH_DAV1D"] = self.options.with_dav1d
        tc.variables["WITH_EXAMPLES"] = False
        tc.variables["WITH_GDK_PIXBUF"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["WITH_JPEG_DECODER"] = self.options.get_safe("with_jpeg", False)
        tc.variables["WITH_JPEG_ENCODER"] = self.options.get_safe("with_jpeg", False)
        tc.variables["WITH_OpenJPEG_DECODER"] = self.options.get_safe("with_openjpeg", False)
        tc.variables["WITH_OpenJPEG_ENCODER"] = self.options.get_safe("with_openjpeg", False)
        tc.variables["WITH_OPENJPH_ENCODER"] = self.options.get_safe("with_openjph", False)
        tc.variables["WITH_OPENH264_DECODER"] = self.options.get_safe("with_openh264", False)
        # Disable finding possible Doxygen in system, so no docs are built
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Doxygen"] = True
        tc.cache_variables["CMAKE_COMPILE_WARNING_AS_ERROR"] = False
        tc.generate()
        deps = CMakeDeps(self)
        if Version(self.version) >= "1.18.0":
            deps.set_property("libde265", "cmake_file_name", "LIBDE265")
            deps.set_property("openjph", "cmake_file_name", "OPENJPH")
        if Version(self.version) >= "1.19.0":
            deps.set_property("openh264", "cmake_file_name", "OpenH264")
        deps.generate()

    def build(self):
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
        self.cpp_info.libs = ["heif"]

        if not self.options.shared:
            self.cpp_info.defines = ["LIBHEIF_STATIC_BUILD"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
            if Version(self.version) >= "1.18.0":
                self.cpp_info.system_libs.append("dl")
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

        if self.options.with_libde265:
            self.cpp_info.requires.append("libde265::libde265")
        if self.options.with_x265:
            self.cpp_info.requires.append("libx265::libx265")
        if self.options.with_libaomav1:
            self.cpp_info.requires.append("libaom-av1::libaom-av1")
        if self.options.with_dav1d:
            self.cpp_info.requires.append("dav1d::dav1d")
        if self.options.get_safe("with_jpeg"):
            self.cpp_info.requires.append("libjpeg::libjpeg")
        if self.options.get_safe("with_openjpeg"):
            self.cpp_info.requires.append("openjpeg::openjpeg")
        if self.options.get_safe("with_openjph"):
            self.cpp_info.requires.append("openjph::openjph")
        if self.options.get_safe("with_openh264"):
            self.cpp_info.requires.append("openh264::openh264")
