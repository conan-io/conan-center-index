from conan import ConanFile
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file, save
from conan.tools.scm import Version
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
        "with_dav1d": [True, False],
        "with_ffmpeg": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_libaomav1": [True, False],
        "with_libde265": [True, False],
        "with_libsvtav1": [True, False],
        "with_openjpeg": [True, False],
        "with_x265": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_dav1d": False,
        "with_ffmpeg": False,
        "with_jpeg": False,
        "with_libaomav1": False,
        "with_libde265": True,
        "with_libsvtav1": False,
        "with_openjpeg": True,
        "with_x265": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.17":
            del self.options.with_libsvtav1
            del self.options.with_jpeg
            del self.options.with_openjpeg
            del self.options.with_ffmpeg

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
        if Version(self.version) >= "1.17":
            if self.options.with_libsvtav1:
                self.requires("libsvtav1/1.7.0")
            if self.options.with_jpeg == "libjpeg":
                self.requires("libjpeg/9e")
            elif self.options.with_jpeg == "libjpeg-turbo":
                self.requires("libjpeg-turbo/3.0.1")
            elif self.options.with_jpeg == "mozjpeg":
                self.requires("mozjpeg/4.1.5")
            if self.options.with_openjpeg:
                self.requires("openjpeg/2.5.0")
            if self.options.with_ffmpeg:
                self.requires("ffmpeg/6.1")

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
        tc.variables["WITH_GDK_PIXBUF"] = False
        if Version(self.version) >= "1.17":
            tc.variables["WITH_SvtEnc"] = self.options.with_libsvtav1
            tc.variables["WITH_JPEG_ENCODER"] = self.options.with_jpeg
            tc.variables["WITH_JPEG_DECODER"] = self.options.with_jpeg
            tc.variables["WITH_OPENJPEG"] = self.options.with_openjpeg
            tc.variables["WITH_FFMPEG"] = self.options.with_ffmpeg
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("libde265", "cmake_file_name", "LIBDE265")
        deps.set_property("x265", "cmake_file_name", "X265")
        deps.set_property("dav1d", "cmake_file_name", "DAV1D")
        deps.set_property("libaom-av1", "cmake_file_name", "AOM")
        deps.set_property("libsvtav1", "cmake_file_name", "SvtEnc")
        deps.set_property("libjpeg", "cmake_file_name", "JPEG")
        deps.set_property("openjpeg", "cmake_file_name", "OpenJPEG")
        deps.set_property("ffmpeg", "cmake_file_name", "FFMPEG")
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        # Use only CMake modules from Conan
        rmdir(self, os.path.join(self.source_folder, "cmake", "modules"))
        # Disable gnome thumbnailer plugin
        save(self, os.path.join(self.source_folder, "gnome", "CMakeLists.txt"), "")
        if Version(self.version) >= "1.17":
            replace_in_file(self, os.path.join(self.source_folder, "libheif", "plugins", "encoder_svt.cc"),
                            '#include "svt-av1/', '#include "')

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
            self.cpp_info.components["heif"].system_libs.extend(["m", "pthread", "dl"])
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
        if Version(self.version) >= "1.17":
            if self.options.with_libsvtav1:
                self.cpp_info.components["heif"].requires.append("libsvtav1::encoder")
            if self.options.with_jpeg == "libjpeg":
                self.cpp_info.components["heif"].requires.append("libjpeg::libjpeg")
            elif self.options.with_jpeg == "libjpeg-turbo":
                self.cpp_info.components["heif"].requires.append("libjpeg-turbo::jpeg")
            elif self.options.with_jpeg == "mozjpeg":
                self.cpp_info.components["heif"].requires.append("mozjpeg::libjpeg")
            if self.options.with_openjpeg:
                self.cpp_info.components["heif"].requires.append("openjpeg::openjpeg")
            if self.options.with_ffmpeg:
                self.cpp_info.components["heif"].requires.append("ffmpeg::avcodec")
